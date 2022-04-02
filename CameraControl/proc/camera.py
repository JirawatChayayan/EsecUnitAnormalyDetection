import cv2 as cv
import enum

class CameraMode(enum.Enum):
    RTSP = 0
    Camera = 1


class Camera:
    def __init__(self,source,mode):
        #self.source = 'rtsp://data_analytic:TcAnTaRa9721&&!@10.158.14.76:554/ch1-s1'
        # self.source = 'rtsp://data_analytic:TcAnTaRa9721xx#@10.153.60.87'
        self.camMode = CameraMode(mode)
        self.source = int(source)
        self.camConnected = False

    def connection(self,width=1366,height=768):
        try:
            if(self.camMode == CameraMode.RTSP):
                self.cam = cv.VideoCapture(self.source,cv.CAP_FFMPEG)
            else:
                self.cam = cv.VideoCapture(self.source)
                self.cam.set(cv.CAP_PROP_FRAME_WIDTH, width)
                self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, height)
            self.camConnected = True
        except Exception as ex:
            print(ex)
            self.camConnected = False
        return self.camConnected

    def disconnect(self):
        if(self.camConnected):
            self.cam.release()

    def delay(self,delay,keys):
        if(self.camConnected):
            return (cv.waitKey(1) & 0xFF == ord(keys))
        return False
    
    
    def grabImg(self):
        if(self.camConnected):
            return self.cam.read()
        return False,[]
    

if __name__ == '__main__':
    cam = Camera(0,CameraMode.Camera)
    cam.connection(1920,1080)
    if(cam.camConnected):
        while True:
            status,img = cam.grabImg()
            if(not status):
                break
            cv.imshow('frame_bgr',img)
            if(cam.delay(1,'q')):
                break
        cam.disconnect()
        cv.destroyAllWindows()
