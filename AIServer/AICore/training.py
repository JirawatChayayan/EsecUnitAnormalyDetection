
from curses.panel import bottom_panel
from logging import exception
from mailcap import findmatch
from re import template
import shutil
from typing import Tuple
from PIL import Image
import io
from sqlalchemy import false
from torch.utils.data import DataLoader
import torch
from AICore.data import StreamingDataset,IMAGENET_MEAN, IMAGENET_STD
from AICore.models import SPADE
import glob
import os
import time
from os.path import expanduser
import cv2 as cv
import matplotlib.pyplot as plt
import base64
import numpy as np
import json
from pathlib import Path

from AICore.computerVision import DefectProcess


class Training():
    def __init__(self):
        self.callbackResult = None
        self.callbackStatus = None
        self.model = None
        self.onTraining = False
        self.initialPath()

        self.templateMat = cv.imread(f'{expanduser("~")}/ImgScreenSave/SetupMode/MatchingROI/Ref3/template.png',0)

    def createDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)

    def initialPath(self):
        self.pathImg = '{}/ImgScreenSave'.format(expanduser("~"))
        self.pathMatching = '{}/SetupMode/MatchingROI'.format(self.pathImg)
        self.pathImgRej = '{}/SetupMode/Reject'.format(self.pathImg)
        self.createDir(self.pathImg)
        self.createDir(self.pathMatching)

    def imgsToBytes(self,imgPath :str,boxCrop : tuple = None):

        print(f"BoxCrop : {boxCrop}")
        img = None
        try:
            img = cv.imread(imgPath,0)
            if(boxCrop is not None):
                result = self.findMatchingPThee(img,boxCrop)
                if(result == None):
                    return None
                #cropImg=rightImg[y:y+h,x:x+w]. 

                # kernel = np.ones((3,3),np.float32)/10
                # dst = cv.filter2D(img,-1,kernel)
                dst = cv.GaussianBlur(img, (3, 3), 0)

                img = dst[result[0]:result[2], result[1]:result[3]]
                #cv.imwrite("cropest-2.jpg",img)
            img = cv.resize(img, (224,224))
            #cv.imwrite('crop.png',img)
            is_success, im_buf_arr = cv.imencode(".png", img)
            img_byte = im_buf_arr.tobytes()
            del img
            # im = Image.open(imgPath)
            # if(boxCrop == None):
            #     img = im
            # else:
            #     x1 = boxCrop[1]
            #     y1 = boxCrop[0]

            #     x2 = boxCrop[3]
            #     y2 = boxCrop[2]
            #     print(boxCrop)
            #     print((x1,y1,x2,y2))
            #     img = im.crop((x1,y1,x2,y2))
            # buf = io.BytesIO()
            # img.resize((224,224))
            # img.save('crop.png',format='png')

            # img.save(buf, format='PNG')
            # img_byte = buf.getvalue()
            return img_byte
        except:
            print(imgPath)
            return None

    def convertImage(self,imgs : list, boxCrop : tuple = None):
        start = time.perf_counter()
        results = []
        a = len(imgs)*1.00
        b = 0.00
        for img in imgs:
            bimg = self.imgsToBytes(img, boxCrop)
            if(bimg is not None):
                results.append(bimg)
            b+=1.00
            self.resultPublish("Convert Image",format((b/a)*100,".3f"),"{} %".format(format((b/a)*100,".3f")))
        end = time.perf_counter()
        print(f'Finished in {round(end-start, 2)} second(s)')
        self.resultPublish("Convert Image",0,f'Finished in {round(end-start, 2)} second(s)')
        return results #self.byteImgS
    
    def findMatching(self,imagefind,imageMat):
        try:
            w, h = imageMat.shape[::-1]
            res = cv.matchTemplate(cv.cvtColor(imagefind,cv.COLOR_BGR2GRAY), imageMat, cv.TM_CCOEFF_NORMED)
            treshole = 0.75
            loc = np.where(res >= treshole)
            for pt in zip(*loc[::-1]):
                if len(pt) == 2:
                    top_left = pt
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    return True,(top_left,bottom_right)
            return False,None
        except:
            return False,None

    def findMatROIRef(self,imagefind,bbox):
        if(self.templateMat is not None):
            self.templateMat = cv.imread(f'{self.pathMatching}/Ref3/template.png',0)
        w, h = self.templateMat.shape[::-1]
        method = eval('cv.TM_CCOEFF')
        res = cv.matchTemplate(imagefind, self.templateMat, method)
    
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        dict_matresult = {
            "topleft": top_left,
            "bottomright": bottom_right
            }

        json_data = json.dumps(dict_matresult, indent=2)
        f = open(f'{self.pathMatching}/Ref1/MatchingData.json', 'w')
        f.write(json_data)
        f.close()

    def findMatchingPThee(self,imagefind,bbox,teach = False):
        if(self.templateMat is not None):
            self.templateMat = cv.imread(f'{self.pathMatching}/Ref3/template.png',0)
        
        #template = self.templateMat
        #shape[::-1]
        w, h = self.templateMat.shape[::-1]
        method = eval('cv.TM_CCOEFF')
        res = cv.matchTemplate(imagefind, self.templateMat, method)
    
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        roi_tpleft = (bbox[1],bbox[0])
        roi_bnright = (bbox[3],bbox[2])

        # print(roi_tpleft,roi_bnright)

        # print(top_left)
        # print(bottom_right)

        ver_offset = top_left[1]-431
        hor_offset = top_left[0]-16
        print(f"Offset Y : {ver_offset}")
        print(f"Offset X : {hor_offset}")

        if (top_left[0] >= 14) and (top_left[0] <=25) or (top_left[0] >= 3) and (top_left[0] <=9):   # ((age>= 8) and (age<= 12))
            
            if(teach):
                os_roi_tpleft = (roi_tpleft[0]-hor_offset,roi_tpleft[1]-ver_offset)
                os_roi_bnright = (roi_bnright[0]-hor_offset, roi_bnright[1]-ver_offset)
            else:
                os_roi_tpleft = (roi_tpleft[0]+hor_offset,roi_tpleft[1]+ver_offset)
                os_roi_bnright = (roi_bnright[0]+hor_offset, roi_bnright[1]+ver_offset)
            # cropped_image = imagefind[os_roi_tpleft[1]:os_roi_bnright[1],os_roi_tpleft[0]:os_roi_bnright[0]]
            # cv.imwrite("cropest.jpg",cropped_image)
            roi = [os_roi_tpleft[1],os_roi_tpleft[0],os_roi_bnright[1],os_roi_bnright[0]]
            print(f"Mat OK {roi}")
            return roi
        else:
            print('Template Position out of Range')
            return None

    def alignROIMatching(self,imagefind,bbox):
        try:
            print(bbox)
            #paths = Path(self.pathMatching)
            res = None
            refPoint = None
            lstDir = os.listdir(self.pathMatching)
            template = cv.imread(f'{self.pathMatching}/Ref1/template.png',0)
            found,res = self.findMatching(imagefind,template)
            f = open(f'{self.pathMatching}/Ref1/MatchingData.json', "r")
            strJson = f.read()
            f.close()
            refPoint = json.loads(strJson)["topleft"]

            print(found)

            # print(lstDir)
            # for folder in lstDir:

            #     pathCombine = f'{self.pathMatching}/{folder}/template.png'
            #     print(pathCombine)

            #     #imageMat = cv.imread(f'{self.pathMatching}/{folder}/template.png',0)
            #     imageMat = cv.imread('/home/esec-ai/ImgScreenSave/SetupMode/MatchingROI/Ref1/template.png',0)
            #     found,res = self.findMatching(imagefind,imageMat)
            #     print(found)
            #     if(found == True):
            #         print(folder)
            #         f = open(f'{self.pathMatching}/{folder}/MatchingData.json', "r")
            #         strJson = f.read()
            #         f.close()
            #         refPoint = json.loads(strJson)["topleft"]
            #         break
            top_left = res[0]
            bottom_right = res[1]
            bbox2 : list = []
            if(res is not None):
                xres = top_left[0] - refPoint[0]
                yres = top_left[1] - refPoint[1]

                print(xres)
                print(yres)
                if (xres < 0 and yres < 0):
                    bbox2.append(bbox[0] + abs(xres))
                    bbox2.append(bbox[1] + abs(yres))
                    bbox2.append(bbox[2] + abs(xres))
                    bbox2.append(bbox[3] + abs(yres))
                elif (xres >= 0 and yres < 0):
                    print("Case 2")
                    bbox2.append(bbox[0] - abs(xres))
                    bbox2.append(bbox[1] + abs(yres))
                    bbox2.append(bbox[2] - abs(xres))
                    bbox2.append(bbox[3] + abs(yres))
                elif (xres < 0 and yres >= 0):
                    bbox2.append(bbox[0] + abs(xres))
                    bbox2.append(bbox[1] - abs(yres))
                    bbox2.append(bbox[2] + abs(xres))
                    bbox2.append(bbox[3] - abs(yres))
                elif (xres >= 0 and yres >= 0):
                    bbox2.append(bbox[0] - abs(xres))
                    bbox2.append(bbox[1] - abs(yres))
                    bbox2.append(bbox[2] - abs(xres))
                    bbox2.append(bbox[3] - abs(yres))
                # print(xres)
                # print(yres)
                # print("TEST")
                return True,bbox2
            return False,None
        except Exception as ex:
            print(ex)
            return False,None

    def train(self,imgs : list, boxCrop : tuple = None):
        #boxCrop (X1, Y1, X2, Y2)
        self.statusPublish("Initialize...","INFO")
        i_count = 0
        if(imgs == None):
            self.statusPublish("Not found image !!!","ERROR")
            raise Exception("imgs is none !!!")
        if(len(imgs) == 0):
            self.statusPublish("Not found image !!!","ERROR")
            raise Exception("Don't have image !!!")
        if(len(imgs) < 20):
            self.statusPublish("Image must be > 20 !!!","ERROR")
            raise Exception("Image must be > 20")
        
        try:
            self.onTraining = True
            image_train = []
            train_dataset = None
            image_train = self.convertImage(imgs,boxCrop)
            if len(image_train) > 2:
                # test dataset will contain 1 test image
                train_dataset = StreamingDataset()
                # train images
                for training_image in image_train:
                    train_dataset.add_pil_image(
                        Image.open(io.BytesIO(training_image))
                    )
                self.statusPublish("Start Training.","INFO")
                self.resultPublish("Training",0,"Start")

                del self.model
                #self.model = SPADE(k=25,backbone_name="wide_resnet50_2",)
                #self.model = SPADE()
                self.model = SPADE(k=int(len(image_train)-1),backbone_name="wide_resnet50_2",)
                self.model.callbackResult = self.resultPublish
                self.model.fit(DataLoader(train_dataset))
                #torch.save(self.model, self.weightFileName())

                #self.predict(imgs[1],boxCrop)

                self.resultPublish("Training",100,"Finished.")
                self.statusPublish("Start Finished.","INFO")
            else:
                self.statusPublish("Can not training this image !!!","ERROR")
            self.onTraining = False
        except Exception as ex:
            self.onTraining = False
            del self.model
            self.statusPublish(str(ex),"ERROR")
            pass

    def deletefileRej(self):
        for filename in os.listdir(self.pathImgRej):
            file_path = os.path.join(self.pathImgRej, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def tensor_to_img(self,x, normalize=False):
        if normalize:
            x *= IMAGENET_STD.unsqueeze(-1).unsqueeze(-1)
            x += IMAGENET_MEAN.unsqueeze(-1).unsqueeze(-1)
        x =  x.clip(0.,1.).permute(1,2,0).detach().numpy()
        return x

    def pred_to_img(self,x, range):
        range_min, range_max = range
        x -= range_min
        if (range_max - range_min) > 0:
            x /= (range_max - range_min)
        return self.tensor_to_img(x)

    def show_pred(self,sample,fmap,currentScore,thresholdAMS = None):
        sample_img = self.tensor_to_img(sample, True)
        fmap_img = self.pred_to_img(fmap, [0,255])*255

        fmap_img[0][0] = 255.0000
        fmap_img[0][1] = 0.0000
        # try:
        #     #print(fmap_img[0][0])
        #     # for x in fmap_img:
        #     #     for y in x:
        #     #         print(y)
        #     #cv.imwrite(('color_img_{}.jpg'.format(time.time())), fmap_img)
        #     #normalized_image = fmap_img*255
        #     #print(normalized_image)
        # except:
        #     pass
        fig = plt.figure()
        plt.imshow(sample_img)
        plt.axis('off')

        bytesImgInput = io.BytesIO()
        fig.savefig(bytesImgInput, format='jpg', bbox_inches='tight', pad_inches=0, transparent=True)
        bytesImgInput.seek(0)
        base64ImgInput = base64.b64encode(bytesImgInput.read())
        strBase64Input = str(base64ImgInput)[2:-1]

        plt.imshow(fmap_img, cmap="jet", alpha=0.5)
        bytesImgHeat = io.BytesIO()
        fig.savefig(bytesImgHeat, format='jpg', bbox_inches='tight', pad_inches=0, transparent=True)
        bytesImgHeat.seek(0)
        base64ImgHeat = base64.b64encode(bytesImgHeat.read())
        strBase64Heat = str(base64ImgHeat)[2:-1]

        print(thresholdAMS)
        print(currentScore)
        if(thresholdAMS is not None):

            if(currentScore > thresholdAMS):
                plt.clf()
                plt.cla()
                plt.axis('off')
                plt.imshow(fmap_img, cmap="gray", alpha=1)
                bytesImgTensor = io.BytesIO()
                fig.savefig(bytesImgTensor, format='png', bbox_inches='tight', pad_inches=0, transparent=False)
                bytesImgTensor.seek(0)
                base64ImgTensor = base64.b64encode(bytesImgTensor.read())
                strBase64Tensor = str(base64ImgTensor)[2:-1]
                strBase64Heat = (DefectProcess()).findDefect(strBase64Tensor,strBase64Heat,thresholdAMS,1)
        
        plt.clf()
        plt.cla()
        plt.axis('off')
        fig.clear()
        
        return "data:image/jpg;base64,{}".format(strBase64Input),"data:image/jpg;base64,{}".format(strBase64Heat)

    def predict(self,imgs,boxCrop : tuple = None,threshold:int = None):
        if(self.model is None or self.onTraining):
            self.statusPublish("not have Model in system !!!","ERROR")
            raise Exception("not have Model in system !!!")
        self.statusPublish("Initialize...","INFO")
        i_count = 0
        if(imgs == None):
            self.statusPublish("Not found image !!!","ERROR")
            raise Exception("imgs is none !!!")
        if(len(imgs) == 0):
            self.statusPublish("Not found image !!!","ERROR")
            raise Exception("Don't have image !!!")
        image_test = self.convertImage(imgs,boxCrop)
        result = []
        test_dataset = StreamingDataset()
        for test_image in image_test:
            test_dataset.add_pil_image(
                Image.open(io.BytesIO(test_image))
            )
        n = 0
        for img in test_dataset:
            sample, *_ = img
            img_lvl_anom,pxl_lvl_anom = self.model.predict(sample.unsqueeze(0))
            score = pxl_lvl_anom.min(),pxl_lvl_anom.max()
            scoreMin = int('{:.0f}'.format(score[0]))
            scoreMax = int('{:.0f}'.format(score[1]))
            imgHeat = None
            imgInput = None
            if(threshold is not None):
                if(scoreMax > threshold):
                    imgInput,imgHeat = self.show_pred(sample,pxl_lvl_anom,scoreMax,threshold)
            if(scoreMin>255):
                scoreMin = 255
            if(scoreMax>255):
                scoreMax = 255
            param = {
                "imgfilename": os.path.basename(imgs[n]),
                "scoreMin" : scoreMin,
                "scoreMax" : scoreMax
            }
            n +=1
            self.resultPublish("Inference",0,param)
            #"resultImgInput" : imgInput,
            #"resultImgHeat" : imgHeat
            param["resultImgInput"] = imgInput
            param["resultImgHeat"] = imgHeat
            result.append(param)
        del test_dataset
        del image_test
        return result

    def predict_disp(self,imgs,boxCrop : tuple = None,threshold = None):
        if(self.model is None or self.onTraining):
            self.statusPublish("not have Model in system !!!","ERROR")
            raise Exception("not have Model in system !!!")
        self.statusPublish("Initialize...","INFO")
        i_count = 0
        if(imgs == None):
            self.statusPublish("Not found image !!!","ERROR")
            raise Exception("imgs is none !!!")
        if(len(imgs) == 0):
            self.statusPublish("Not found image !!!","ERROR")
            raise Exception("Don't have image !!!")
        image_test = self.convertImage(imgs,boxCrop)
        result = []
        test_dataset = StreamingDataset()
        for test_image in image_test:
            test_dataset.add_pil_image(
                Image.open(io.BytesIO(test_image))
            )
        n = 0
        acm = 120 # Anomaly Score Max
        pixel_count_max = 100
        for img in test_dataset:
            sample, *_ = img
            img_lvl_anom,pxl_lvl_anom = self.model.predict(sample.unsqueeze(0))
            score = pxl_lvl_anom.min(),pxl_lvl_anom.max()
            scoreMin = int('{:.0f}'.format(score[0]))
            scoreMax = int('{:.0f}'.format(score[1]))
            imgInput,imgHeat =  self.show_pred(sample, pxl_lvl_anom,scoreMax,threshold)

            #print(score)
            if(scoreMin>255):
                scoreMin = 255
            if(scoreMax>255):
                scoreMax = 255
            #print(scoreMin,scoreMax)
            # print(pxl_lvl_anom[pxl_lvl_anom>acm])
            # if torch.numel(pxl_lvl_anom[pxl_lvl_anom>acm]) > pixel_count_max:
            #     print("Count pixel > max")
            # else:
            #     print("Reject")

            param = {
                "imgfilename": os.path.basename(imgs[n]),
                "scoreMin" : scoreMin,
                "scoreMax" : scoreMax
            }
            n +=1
            self.resultPublish("Inference",0,param)
            #"resultImgInput" : imgInput,
            #"resultImgHeat" : imgHeat
            param["resultImgInput"] = imgInput
            param["resultImgHeat"] = imgHeat
            result.append(param)
            

        del test_dataset
        del image_test
        return result

    def resultPublish(self,status,percentage = 0,message = ""):
        param = {
            "status":status,
            "percentage" : percentage,
            "message": message
        }
        if(self.callbackResult is None):
            print(param)
        else:
            self.callbackResult(param)

    def statusPublish(self,msg,status):
        if(self.callbackStatus is None):
            print('{} {}'.format(status,msg))
        else:
            self.callbackStatus(msg,status)


def listImage():
    list = glob.glob('{}{}/*.png'.format(expanduser("~"),'/Img'))
    return list

if __name__ == '__main__':
    train = Training()
    train.train(listImage(),(690,490,915,712))