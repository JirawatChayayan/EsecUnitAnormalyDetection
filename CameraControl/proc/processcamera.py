import cv2 as cv
import time
import os
import threading
from proc.mqtt import MQTT
from proc.serialConnect import TriggerCommunication,ModeRun
from proc.camera import Camera,CameraMode
from os.path import expanduser

class ProcessCamera:
    def __init__(self):
        self.initialPath()
        self.cam = Camera(0,CameraMode.Camera)
        self.saveThisImageProc = False
        self.trig = TriggerCommunication()
        self.trig.callbacksProcess = self.callbackProc
        self.trig.callbacksTest = self.callbackTest
        self.trig.callbacksTrain = self.callbackTrain
        self.threadRead = threading.Thread(target=self.processLoop)
        self.stopped = threading.Event()
        self.mqtt = MQTT()
        self.saveThisImageAPITest = False
        self.saveThisImageAPITrain = False
    
    def callbackProc(self):
        self.saveThisImageProc = True
    
    def callbackTest(self):
        self.saveThisImageAPITest = True
    
    def callbackTrain(self):
        self.saveThisImageAPITrain = True

    def capture(self):
        if(self.cam.camConnected):
            status,img = self.cam.grabImg()
        if(status):
            return img

    def trigger(self):
        self.saveThisImage = True

    def createDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def initialPath(self):
        pathMain =  '{}/ImgScreenSave'.format(expanduser("~"))
        pathSetup = '{}/SetupMode'.format(pathMain)
        pathProcess = '{}/ProcessMode'.format(pathMain)
        pathSetupTrain = '{}/Train'.format(pathSetup)
        pathSetupTest = '{}/Test'.format(pathSetup)
        self.createDir(pathMain)
        self.createDir(pathSetup)
        self.createDir(pathProcess)
        self.createDir(pathSetupTrain)
        self.createDir(pathSetupTest)
        return pathMain,pathSetup,pathProcess,pathSetupTrain,pathSetupTest

    def selectDir(self,mode = None):
        pathMain,pathSetup,pathProcess,pathSetupTrain,pathSetupTest = self.initialPath()
        if(mode == ModeRun.Setup):
            return pathSetup
        elif(mode == ModeRun.Process):
            return pathProcess
        else:
            return pathMain
    
    def setupDir(self,Train = True):
        pathMain,pathSetup,pathProcess,pathSetupTrain,pathSetupTest = self.initialPath()
        if(Train):
            return pathSetupTrain
        else:
            return pathSetupTest

    def saveImg(self,img,mode):
        path = self.selectDir(mode)+'/'+(str(time.time()).replace('.','_'))+'.png'
        cv.imwrite(path,img)
        self.mqtt.sendGrabSignal(mode,path)
        print ('Save img at {}'.format(path))

    def saveImgSetup(self,img,Train = True):
        path = self.setupDir(Train)+'/'+(str(time.time()).replace('.','_'))+'.png'
        cv.imwrite(path,img)
        self.mqtt.sendGrabSignal(ModeRun.Setup,path)
        print ('Save img at {}'.format(path))

    def connect(self):
        self.initialPath()
        self.mqtt.connectMqtt()
        self.cam.connection(1280,720)
        if(self.cam.camConnected == False):
            self.disconnect()
            return False
        self.trig.openSerialPort()
        if(self.trig.serialHandle == None):
            self.disconnect()
            return False
        if(self.trig.serialHandle.is_open == False):
            self.disconnect()
            return False
        self.threadRead.start()

    
    def disconnect(self):
        self.stopped.set()
        time.sleep(2)
        try:
            self.cam.disconnect()
        except:
            pass
        try:
            self.trig.closeSerialPort()
            self.mqtt.disconnectMQTT()
        except:
            pass


    def processLoop(self):
        try:
            while not self.stopped.is_set():
                img = self.capture()
                key = cv.waitKey(1)
                if(self.saveThisImageProc):
                    try:
                        self.saveImg(img,ModeRun.Process)
                        self.saveThisImageProc = False
                    except Exception as e:
                        print(e)
                        pass
                if(self.saveThisImageAPITest):
                    try:
                        self.saveImgSetup(img,False)
                        self.saveThisImageAPITest = False
                    except Exception as e:
                        print(e)
                        pass
                if(self.saveThisImageAPITrain):
                    try:
                        self.saveImgSetup(img,True)
                        self.saveThisImageAPITrain = False
                    except Exception as e:
                        print(e)
                        pass
                if(key == ord('q')):
                    break
                elif(key == ord('s')):
                    self.trig.sendSerial(False)
                elif(key == ord('p')):
                    self.trig.sendSerial(True)
                pass
            print('close')
            cv.destroyAllWindows()
            self.disconnect()

        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            cv.destroyAllWindows()
            self.disconnect()
        except:
            print('Error')
            cv.destroyAllWindows()
            self.disconnect()
       
        