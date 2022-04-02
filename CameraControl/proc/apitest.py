from proc.camera import CameraMode,Camera
from proc.serialConnect import TriggerCommunication,ModeRun
import cv2 as cv
import time
import os

cam = Camera(0,CameraMode.Camera)

saveThisImg = False

def Capture():
    if(cam.camConnected):
        status,img = cam.grabImg()
        if(status):
            return img

def Trigger():
    global saveThisImg
    saveThisImg = True

def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def selectDir(mode = None):
    pathMain = '/home/j/ImgScreenSave'
    pathSetup = '{}/SetupMode'.format(pathMain)
    pathProcess = '{}/ProcessMode'.format(pathMain)
    createDir(pathMain)
    createDir(pathSetup)
    createDir(pathProcess)
    if(mode == ModeRun.Setup):
        return pathSetup
    elif(mode == ModeRun.Process):
        return pathProcess
    else:
        return pathMain

def saveImg(img,mode):
    path = selectDir(mode)+'/'+str(time.time())+'.png'
    cv.imwrite(path,img)
    print ('Save img at {}'.format(path))

if __name__ == '__main__':
    selectDir()
    cam.connection(1280,720)
    try:
        if(cam.camConnected):
            trig = TriggerCommunication()
            trig.subscribe(Trigger)
            trig.openSerialPort()
            while True:
                img = Capture()
                key = cv.waitKey(1)
                if(saveThisImg):
                    try:
                        saveImg(img,trig.modeRun)
                        saveThisImg = False
                    except:
                        pass
                if(key == ord('q')):
                    break
                elif(key == ord('s')):
                    trig.sendSerial(False)
                elif(key == ord('p')):
                    trig.sendSerial(True)
            cam.disconnect()
            cv.destroyAllWindows()
            trig.closeSerialPort()
    except KeyboardInterrupt:
        cam.disconnect()
        cv.destroyAllWindows()
        trig.closeSerialPort()
    except:
        cam.disconnect()
        cv.destroyAllWindows()
        trig.closeSerialPort()