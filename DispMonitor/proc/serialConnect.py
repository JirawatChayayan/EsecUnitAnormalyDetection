
from datetime import datetime
import threading
import time
import serial
import sys
import json
import enum
import re
import random

class SerialDispCommunication:
    def __init__(self):
        self.port = '/dev/ttyUSB0'
        if(sys.platform == 'win32'):
            self.port = 'COM17'
        self.buadrate = 115200
        self.serialHandle = None
        self.stopped = None
        self.threadRead = None
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
                    time.sleep(5)
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
            time.sleep(5)

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
        
    def readSerial(self):
        print('Serial Ready')
        while not self.stopped.is_set() and (self.serialHandle is not None):
            try:
                cc=str(self.serialHandle.readline())
                cleanMsg = cc[2:][:-5]
                #splitData = cleanMsg.split(';')
                print(cleanMsg)
            except KeyboardInterrupt: #Capture Ctrl-C
                print ("Captured Ctrl-C")
                self.stopped.set()
                return None
        del self.stopped
        del self.threadRead
        
    def sendRate(self,rate):
        cmd = ":Rate:{}\n".format(rate)
        if(self.serialHandle is not None):
            self.serialHandle.write(cmd.encode())
    
    def sendIP(self,ip):
        cmd = ":IP:{}\n".format(ip)
        if(self.serialHandle is not None):
            self.serialHandle.write(cmd.encode())
    
    def sendAlarm(self,alarm):
        cmdAlarmState = "true"
        if(not alarm):
            cmdAlarmState = "false"
        cmd = ":Alarm:{}\n".format(cmdAlarmState)
        if(self.serialHandle is not None):
            self.serialHandle.write(cmd.encode())
    
    def sendAllData(self,alarm,rate,triger,ip):
        cmdAlarmState = "true"
        if(not alarm):
            cmdAlarmState = "false"
        cmd = ":{}:{}:{}:{}\n".format(cmdAlarmState,rate,triger,ip)
        if(self.serialHandle is not None):
            self.serialHandle.write(cmd.encode())

    def send_3_Data(self,alarm,rate,triger):
        cmdAlarmState = "true"
        if(not alarm):
            cmdAlarmState = "false"
        cmd = ":{}:{}:{}\n".format(cmdAlarmState,rate,triger)
        if(self.serialHandle is not None):
            self.serialHandle.write(cmd.encode())
        
        
def trig():
    print('{} Recived Signal'.format(datetime.utcnow()))

if __name__ == "__main__":
    Trig = SerialDispCommunication()
    Trig.openSerialPort()
    try:
        # i = 0
        while(True):
            # if(i>2000):
            #     i = 0
            # i+=1
            rate =  int(random.random()*1000)
            ip =  "{}.{}.{}.{}".format(int(random.random()*100),int(random.random()*100),int(random.random()*100),int(random.random()*100))
            state = random.random()>0.5
            
            triger = int(random.random()*100)
            # Trig.sendRate(rate)
            # Trig.sendIP(ip)
            # Trig.sendAlarm(state)
            Trig.sendAllData(state,rate,triger,ip)
            time.sleep(0.05) 
            
            
    except KeyboardInterrupt:
        Trig.closeSerialPort()
        time.sleep(0.5)
        pass
