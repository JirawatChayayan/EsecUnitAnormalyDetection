import cv2 as cv
import time
import os
import threading
from proc.mqtt import MQTT
from proc.serialConnect import TriggerCommunication,ModeRun
from proc.camera import Camera,CameraMode
from os.path import expanduser
import numpy as np
import queue
from datetime import datetime
import sys

class ProcessCamera:
    def __init__(self):
        self.initialPath()
        self.cam = Camera(0,CameraMode.Camera)
        self.saveThisImageProc = False
        self.trig = TriggerCommunication()
        self.trig.callbacksProcess = self.callbackProc
        self.trig.callbacksTest = self.callbackTest
        self.trig.callbacksTrain = self.callbackTrain
        self.trig.callbackRate = self.callbackRate
        self.threadRead = threading.Thread(target=self.processLoop)
        self.stopped = threading.Event()
        self.mqtt = MQTT()
        self.saveThisImageAPITest = False
        self.saveThisImageAPITrain = False
        self.saveBackupImg = True
        self.averagePixel = 75.0
        self.errorImageCounter = 0
        self.errorImageCounterLimit = 50
    
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

    def callbackRate(self,rate,stopmc,trigCount,ip):
        self.mqtt.sendRate(rate,stopmc,trigCount,ip)

    def trigger(self):
        self.saveThisImage = True

    def createDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def initialPath(self):
        self.pathMain =  '{}/ImgScreenSave'.format('/home/esec-ai') #expanduser("~")
        self.pathSetup = '{}/SetupMode'.format(self.pathMain)
        self.pathProcess = '{}/ProcessMode'.format(self.pathMain)
        self.pathSetupTrain = '{}/Train'.format(self.pathSetup)
        self.pathSetupTest = '{}/Test'.format(self.pathSetup)
        self.pathSetupReject = '{}/Reject'.format(self.pathSetup)
        now = datetime.now()
        self.pathTempolaryTest = '{}/TempolaryTest/{}-{}-{}'.format(self.pathSetup,now.day,now.month,now.year)
        self.createDir(self.pathMain)
        self.createDir(self.pathSetup)
        self.createDir(self.pathProcess)
        self.createDir(self.pathSetupTrain)
        self.createDir(self.pathSetupTest)
        self.createDir(self.pathSetupReject)
        self.createDir(self.pathTempolaryTest)

    def selectDir(self,mode = None):
        self.initialPath()
        if(mode == ModeRun.Setup):
            return self.pathSetup
        elif(mode == ModeRun.Process):
            return self.pathProcess
    
    def setupDir(self,Train = True):
        self.initialPath()
        if(Train):
            return self.pathSetupTrain
        else:
            return self.pathSetupTest

    def findImageShifting(self,img):
        ret , dst = cv.threshold (img,5,255,cv.THRESH_BINARY_INV) 
        contours, _ = cv.findContours(dst, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        self.initialPath()
        for c in contours:
            rect = cv.boundingRect(c)
            if rect[2] < 10 or rect[3] < 10: continue

            #reject save
            print("Image Shift")
            #self.saveBakImg(img)
            return False
        return True

    def saveBakImg(self,img,fName = None):
        try:
            self.initialPath()
            if(fName == None):
                fName = (str(time.time()).replace('.','_'))+'.jpg'
            fName = fName.replace('.png','.jpg')
            if(self.saveBackupImg):
                pathBak = self.pathTempolaryTest +'/'+fName
                cv.imwrite(pathBak,img)
        except:
            pass

    def saveImg(self,img,mode):
        self.saveBakImg(img)
        avg = np.average(img)
        print(avg)
        if(avg <= self.averagePixel):
            # self.errorImageCounter += 1
            # print(f"Image Error {self.errorImageCounter}")
            return
        if(self.findImageShifting(img)== False):
            # print(f"Image Error {self.errorImageCounter}")
            # self.errorImageCounter += 1
            return
        # self.errorImageCounter = 0
        self.initialPath()
        fName = (str(time.time()).replace('.','_'))+'.png'
        path = self.selectDir(mode)+'/'+fName
        cv.imwrite(path,img)
        self.mqtt.sendGrabSignal(mode,path)
        print ('Save img at {}'.format(path))

    def saveImgSetup(self,img,Train = True):
        avg = np.average(img)
        print(avg)
        if(avg <= self.averagePixel):
            return
        self.initialPath()
        if(self.findImageShifting(img)== False):
            return
        fName = (str(time.time()).replace('.','_'))+'.png'
        path = self.setupDir(Train)+'/'+ fName
        cv.imwrite(path,img)
        self.mqtt.sendGrabSignal(ModeRun.Setup,path)
        print ('Save img at {}'.format(path))

    def connect(self):
        self.initialPath()
        self.mqtt.connectMqtt()
        self.cam.connection(640,480)
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
            # imgQueue = queue.Queue(60)
            # for i in range(0,62):
            #     img = self.capture()
            #     imgQueue.put(img)
            #     key = cv.waitKey(1)
            while not self.stopped.is_set():
                # if(self.errorImageCounter > self.errorImageCounterLimit):
                #     break
                img = self.capture()
                
                avg = np.average(img)
                print(avg)

                #imgQueue.put(img)
                key = cv.waitKey(1)
                if(self.saveThisImageProc):
                    try:
                        self.saveImg(img,ModeRun.Process)
                        self.saveThisImageProc = False
                    except Exception as e:
                        self.cam.disconnect()
                        time.sleep(5)
                        print(e)
                        self.cam.connection(640,480)
                        pass
                if(self.saveThisImageAPITest):
                    try:
                        self.saveImgSetup(img,False)
                        self.saveThisImageAPITest = False
                    except Exception as e:
                        self.cam.disconnect()
                        time.sleep(5)
                        print(e)
                        self.cam.connection(640,480)
                        pass
                if(self.saveThisImageAPITrain):
                    try:
                        self.saveImgSetup(img,True)
                        self.saveThisImageAPITrain = False
                    except Exception as e:
                        self.cam.disconnect()
                        time.sleep(5)
                        print(e)
                        self.cam.connection(640,480)
                        pass
                if(key == ord('q')):
                    break
                elif(key == ord('s')):
                    self.trig.sendSerial(False)
                elif(key == ord('p')):
                    self.trig.sendSerial(True)
                pass
            print('close')
            # if(self.errorImageCounter > self.errorImageCounterLimit):
            #     sys.exit()
                # os._exit(0)
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
       
        