from math import pi
import time
import cv2 as cv
import numpy as np
import os





def FindPixelDefect(imgTensor,imgPaint,ams,percentReject):
    img_gray  = cv.cvtColor(imgTensor,cv.COLOR_BGR2GRAY)
    img_color = imgPaint
    img_gray_crop = img_gray[5:50, 5:50]
    img_crop_avg = int(np.average(img_gray_crop))
    if(img_crop_avg > ams):
        img_crop_avg = ams-5
    img_gray[0][0] = img_crop_avg
    img_gray[0][1] = img_crop_avg
    allPixel = np.sum(img_gray >= 0)
    percentFactor = 100.00/allPixel
    val = ams+1
    if(val>255):
        val = 255
    (T, threshInv) = cv.threshold(img_gray, val, 255,cv.THRESH_BINARY)
    thresPixel = np.sum(threshInv>= 200)
    
    pixelDefectPercent = thresPixel*percentFactor
    print(f'pixel defect count : {thresPixel}')
    print(f'pixel All : {allPixel}')
    print(f'pixel defect percent : {pixelDefectPercent}')

    edged = cv.Canny(threshInv, 0, 255)
    cnts, _ = cv.findContours(edged, cv.RETR_EXTERNAL , cv.CHAIN_APPROX_NONE)
    IsReject = False
    if(pixelDefectPercent > percentReject):
        IsReject = True
    for cnt in cnts:            
        if(IsReject):    
            img_color = cv.drawContours(img_color, cnt, -1, (0,0,255), 2, cv.LINE_4)
        else:
            img_color = cv.drawContours(img_color, cnt, -1, (0,255,0), 2, cv.LINE_4)
    return img_color





def FindPositionDefect(imgTensor,imgPaint,ams,rejectPercent):
    img_gray  = cv.cvtColor(imgTensor,cv.COLOR_BGR2GRAY)
    img_color = imgPaint
    
    img_gray_crop = int(np.average(img_gray))
    try:
        img_gray_crop = img_gray[5:50, 5:50]
        img_crop_avg = int(np.average(img_gray_crop))
    except:
        img_gray_crop = int(np.average(img_gray))
        pass
    if(img_crop_avg > ams):
        img_crop_avg = ams-5
        if(img_crop_avg < 0):
            img_crop_avg = 0
    img_gray[0][0] = img_crop_avg
    img_gray[0][1] = img_crop_avg

    allPixel = np.sum(img_gray >= 0)
    percentFactor = 100.00/allPixel
    val = ams+1
    if(val>255):
        val = 255
    (T, threshInv) = cv.threshold(img_gray, val, 255,cv.THRESH_BINARY)
    edged = cv.Canny(threshInv, 0, 255)
    cnts, _ = cv.findContours(edged, cv.RETR_EXTERNAL , cv.CHAIN_APPROX_NONE)

    IsReject = False
    areaDefectAll = []
    for cnt in cnts:
        #size = cv.contourArea(cnt)
        x,y,w,h = cv.boundingRect(cnt)
        size = w*h
        print(size)
        if(size <10):
            continue
        else:
            #crop section and counter pixel
            #img_color = cv.rectangle(img_color,(x-3,y-3),(x+3+w,y+3+h),(255,0,0),1)
            imgCrop = img_gray[y:y+h,x:x+w]


            (_, th_crop) = cv.threshold(imgCrop, val, 255,cv.THRESH_BINARY)
            
            cv.imshow("imThreshold",th_crop)
            cv.imshow("imCrop",imgCrop)
            cv.waitKey(0)


            areaPixel = np.sum(th_crop>= 200)
            areaPercent = areaPixel*percentFactor
            del imgCrop
            del th_crop
            areaDefectAll.append(areaPercent)
            print("defect area percent {:.3f} %".format(areaPercent))
            
            if(areaPercent>rejectPercent):
                IsReject = True
                #red
                img_color = cv.drawContours(img_color, cnt, -1, (0,0,128), 2, cv.LINE_4)
                pass
            else:
                img_color = cv.drawContours(img_color, cnt, -1, (0,128,0), 2, cv.LINE_4)
                #green
                pass
    maxLen = 0
    if(len(areaDefectAll)>0):
        maxLen = max(areaDefectAll)

    return img_color,IsReject,maxLen



img = cv.imread('test.jpg',cv.IMREAD_COLOR)

t1 = time.time()
resImg,isReject,areaMax = FindPositionDefect(img,img,120,0.25)
print(f"IsReject : {isReject}")
print(f"AreaMax : {areaMax}")


t2 = time.time()
print(t2-t1)
cv.imshow("img",resImg)
cv.waitKey(0)
cv.destroyAllWindows()
