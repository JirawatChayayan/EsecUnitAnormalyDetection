import cv2 as cv
import numpy as np
import base64


class DefectProcess:
    def __init__(self):
        return

    def readb64(self,b64):
        im_bytes = base64.b64decode(b64)
        im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
        img = cv.imdecode(im_arr, flags=cv.IMREAD_COLOR)
        return img

    def writeb64(self,image):
        retval, buffer = cv.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer)
        return str(jpg_as_text)[2:-1]

    def findDefect(self,b64imgTensor,b64imgPaint,anormalyMaxScore,rejectPercent):
        #print(b64imgTensor)
        imgT = self.readb64(b64imgTensor)
        imgP = self.readb64(b64imgPaint)
        res = self.FindAreaDefect(imgT,imgP,anormalyMaxScore,rejectPercent)
        b64 = self.writeb64(res)
        return b64

    def FindAreaDefect(self,imgTensor,imgPaint,anormalyMaxScore,rejectPercent):
        img_gray  = cv.cvtColor(imgTensor,cv.COLOR_BGR2GRAY)
        img_color = imgPaint
        shape = np.shape(img_gray)[:2]
        percentFactor = (shape[0]*shape[1])/100.00
        (T, threshInv) = cv.threshold(img_gray, anormalyMaxScore+1, 255,cv.THRESH_BINARY)
        edged = cv.Canny(threshInv, 0, 255)
        cnts, _ = cv.findContours(edged, cv.RETR_EXTERNAL , cv.CHAIN_APPROX_NONE)

        for cnt in cnts:
            size = cv.contourArea(cnt)
            if(size <8):
                continue
            else:
                x,y,w,h = cv.boundingRect(cnt)
                img_color = cv.rectangle(img_color,(x-3,y-3),(x+3+w,y+3+h),(255,0,0),1)
                defectPercent = size/percentFactor
                print("defect area percent {:.3f} %".format(defectPercent))
                if(defectPercent > rejectPercent):    
                    img_color = cv.drawContours(img_color, cnt, -1, (0,0,255), 1, cv.LINE_4)
                else:
                    img_color = cv.drawContours(img_color, cnt, -1, (0,255,0), 1, cv.LINE_4)
                #print(f"defect Size : {size}")
        return img_color
