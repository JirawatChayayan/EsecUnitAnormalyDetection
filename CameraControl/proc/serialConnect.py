
from datetime import datetime
import threading
import time
import serial
import sys
import json
import enum
from proc.getip import GetIPAddress
#from getip import GetIPAddress
import re

class ModeRun(enum.Enum):
    Setup = 1
    Process = 2

class TriggerCommunication:
    def __init__(self):
        self.port = '/dev/ttyACM0'
        if(sys.platform == 'win32'):
            self.port = 'COM3'
        self.buadrate = 9600
        self.serialHandle = None
        self.stopped = None
        self.threadRead = None
        self.callbacksProcess = None
        self.callbacksTrain = None
        self.callbacksTest = None
        self.modeRun = ModeRun.Setup
        self.lastJsonConfig = ""
        self.lastStateStopMC = False
        pass
    def openSerialPort(self,isReconnect = False):
        self.serialHandle = None

        while(True):
            try:
                self.serialHandle = serial.Serial(self.port, self.buadrate)
                if(self.serialHandle.is_open):
                    print('Opened Serial')
                    time.sleep(2)
                    self.sendInformation()
                    time.sleep(2)
                    self.sendInformation()
                    time.sleep(2)
                    self.sendStopMachine(self.lastStateStopMC)
                    time.sleep(2)
                    self.sendStopMachine(self.lastStateStopMC)
                    if((not isReconnect)):
                        self.stopped = threading.Event()
                        self.threadRead = threading.Thread(target=self.readSerial)
                        self.threadRead.start()
                    break
            except serial.SerialException as msg:
                print( "Error opening serial port %s" % msg)
                self.serialHandle = None
            except:
                exctype, errorMsg = sys.exc_info()[:2]
                print ("%s  %s" % (errorMsg, exctype))
                self.serialHandle = None

    def closeSerialPort(self,isSet=True):
        try:
            if(isSet):
                self.stopped.set()
            time.sleep(2)
            self.serialHandle.close()
            self.serialHandle.close()
            self.serialHandle.close()
            self.serialHandle.close()
            del self.serialHandle
            self.serialHandle = None
            print('Closed Serial')
        except:
            pass

    def reconnect(self):
        try:
            self.lastJsonConfig = ""
            print('Reconnect Serial')
            self.closeSerialPort()
            time.sleep(10)
            del self.threadRead
            self.threadRead =None
            self.openSerialPort()
        except:
            pass
        
    def sendSerial(self,mode):
        if(self.serialHandle is not None):
            if(mode == ModeRun.Process):
                self.modeRun = ModeRun.Process
                self.serialHandle.write(("{\"Mode\":\"Process\"}"+"\n").encode())
            else:
                self.modeRun = ModeRun.Setup
                self.serialHandle.write(("{\"Mode\":\"Setup\"}"+"\n").encode())
            #self.serialHandle.write("\n".encode())
    def readSerial(self):
        print('Serial Ready')
        t1 = time.time()
        while not self.stopped.is_set():
            try:
                tHancheck = (time.time() - t1)
                if(tHancheck >5):
                    print('{} > Device Hang {}'.format(datetime.utcnow(),tHancheck))
                    self.reconnect()
                cc=str(self.serialHandle.readline())
                cleanMsg = cc[2:][:-5]
                splitData = cleanMsg.split(';')
                if(splitData[0]== 'Trig'):
                    cmd = json.loads(splitData[1])
                    #print('Trigger From Mode : {0}'.format(cmd['Mode']))
                    if(cmd['Mode'] == 'SetupTrain'):
                        if(self.callbacksTrain is not None):
                            self.callbacksTrain()
                    elif(cmd['Mode'] == 'SetupTest'):
                        if(self.callbacksTest is not None):
                            self.callbacksTest()
                    else:
                        if(self.callbacksProcess is not None):
                            self.callbacksProcess()
                    #t1 = time.time()
                else:
                    print('{} > {}'.format(datetime.utcnow(), cleanMsg))
                    if(re.search('HandCheck',cleanMsg) is not None):
                        cmd = json.loads(splitData[1])
                        self.lastStateStopMC = cmd['StopMC']
                        #print('Status Stop Machine : {}'.format(self.lastStateStopMC))
                        t1 = time.time()


            except KeyboardInterrupt: #Capture Ctrl-C
                print ("Captured Ctrl-C")
                self.stopped.set()
                t1 = time.time()
                return None
                break
            
            except:
                exctype, errorMsg = sys.exc_info()[:2]
                print ("Error reading port - %s" % errorMsg)
                self.reconnect()
                t1 = time.time()
                    
        del self.stopped
        del self.threadRead

    def sendInformation(self,machineID = 'ESEC-99P'):
        ip,mac = GetIPAddress().getIt()
        print('IP {} MAC {}'.format(ip,mac))
        obj = {
            'IP' : ip,
            'MAC' : mac,
            'MC_ID'  : machineID.strip()
        }
        strJson = json.dumps(obj)+"\n"
        # if(self.lastJsonConfig  == strJson):
        #     print('Same Data {}'.format(strJson))
        #     return
        # else:
        #     self.lastJsonConfig = strJson
        if(self.serialHandle is not None):
            print('Write Data {}'.format(strJson))
            self.serialHandle.write((strJson).encode())
        pass

    def sendStopMachine(self,stop):
        obj = {
            "StopMC":stop
        }
        strJson = json.dumps(obj)+"\n"
        if(self.serialHandle is not None):
            #self.lastStateStopMC = stop
            #print('Write Data {}'.format(strJson))
            self.serialHandle.write((strJson).encode())

    def setIO(self,ch):
        obj = {
            "SetOutput":ch
        }
        strJson = json.dumps(obj)+"\n"
        if(self.serialHandle is not None):
            #print('Write Data {}'.format(strJson))
            self.serialHandle.write((strJson).encode())

    def resetIO(self,ch):
        obj = {
            "ResetOutput":ch
        }
        strJson = json.dumps(obj)+"\n"
        if(self.serialHandle is not None):
            #print('Write Data {}'.format(strJson))
            self.serialHandle.write((strJson).encode())

    def AllIO(self,on = False):
        obj = {
            "AllOutput":on
        }
        strJson = json.dumps(obj)+"\n"
        if(self.serialHandle is not None):
            #print('Write Data {}'.format(strJson))
            self.serialHandle.write((strJson).encode())


def trig():
    print('{} Recived Signal'.format(datetime.utcnow()))

if __name__ == "__main__":
    Trig = TriggerCommunication()
    Trig.callbacksProcess = trig
    Trig.openSerialPort()
    try:
        i = 0
        lastState = False
        
        while(True):
            time.sleep(5)
            Trig.sendStopMachine(lastState)
            # time.sleep(0.1)
            # Trig.sendInformation()
            lastState = not lastState
            i+=1
            if(i > 6):
                i= 1
                Trig.sendInformation()
                time.sleep(5)
                print('{} Update'.format(datetime.utcnow()))

    except:
        pass
    #a = input()
    Trig.closeSerialPort()