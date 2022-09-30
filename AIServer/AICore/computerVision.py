import cv2 as cv
import numpy as np
import base64


class DefectProcess:
    def __init__(self):
        self.imgtype = "data:image/jpg;base64"
        return

    def readb64(self,b64):
        datasplit = b64.split(",")
        img_b64 = ""
        if(len(datasplit) == 2):
            img_b64 = datasplit[1].strip()
        elif(len(datasplit) == 1):
            img_b64 = b64
        else:
            raise Exception("Image format error")
        im_bytes = base64.b64decode(img_b64)
        im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
        img = cv.imdecode(im_arr, flags=cv.IMREAD_COLOR)
        return img

    def writeb64(self,image):
        retval, buffer = cv.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer)
        return self.imgtype+","+str(jpg_as_text)[2:-1]

    def findDefect(self,b64imgTensor,b64imgPaint,anormalyMaxScore,rejectPercent):
        #print(b64imgTensor)
        imgT = self.readb64(b64imgTensor)
        imgP = self.readb64(b64imgPaint)
        res,isReject,percent = self.FindAreaDefect(imgT,imgP,anormalyMaxScore,rejectPercent)
        b64 = self.writeb64(res)
        return b64,isReject,percent
    
    def findPixel(self,b64imgTensor,b64imgPaint,anormalyMaxScore,rejectPercent):
        #print(b64imgTensor)
        imgT = self.readb64(b64imgTensor)
        imgP = self.readb64(b64imgPaint)
        res,isReject,percent = self.FindPixelDefect(imgT,imgP,anormalyMaxScore,rejectPercent)
        b64 = self.writeb64(res)
        return b64,isReject,percent


    def FindPixelDefect(self,imgTensor,imgPaint,ams,percentReject):
        img_gray  = cv.cvtColor(imgTensor,cv.COLOR_BGR2GRAY)
        img_color = imgPaint

        #interpolation 2 pixel image
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
                img_color = cv.drawContours(img_color, cnt, -1, (0,150,0), 2, cv.LINE_4)
        return img_color,IsReject,pixelDefectPercent


    def FindAreaDefect(self,imgTensor,imgPaint,ams,rejectPercent):
        img_gray  = cv.cvtColor(imgTensor,cv.COLOR_BGR2GRAY)
        img_color = imgPaint

        #interpolation 2 pixel image
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
                
                areaPixel = np.sum(th_crop>= 200)
                areaPercent = areaPixel*percentFactor
                del imgCrop
                del th_crop
                areaDefectAll.append(areaPercent)
                print("defect area percent {:.3f} %".format(areaPercent))
                
                if(areaPercent>rejectPercent):
                    IsReject = True
                    #red
                    img_color = cv.drawContours(img_color, cnt, -1, (0,0,255), 2, cv.LINE_4)
                    pass
                else:
                    img_color = cv.drawContours(img_color, cnt, -1, (0,150,0), 2, cv.LINE_4)
                    #green
                    pass
        maxLen = 0
        if(len(areaDefectAll)>0):
            maxLen = max(areaDefectAll)

        return img_color,IsReject,maxLen

