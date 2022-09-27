import time
import cv2 as cv
import numpy as np
import os




def FindAreaDefect(imgTensor,imgPaint,anormalyMaxScore,rejectPercent):
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






img = cv.imread('test.jpg',cv.IMREAD_COLOR)

t1 = time.time()
resImg = FindAreaDefect(img,img,120,0.25)
t2 = time.time()
print(t2-t1)
cv.imshow("img",resImg)
cv.waitKey(0)
cv.destroyAllWindows()
