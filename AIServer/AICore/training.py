
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

from model import bbox,InferModel,TrainingModel


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

    def imgsToBytes(self,imgPath :str,boxCrop : bbox = None):
        img = None
        try:
            img = cv.imread(imgPath,0)
            if(boxCrop is not None):
                result = self.findMatchingPThee(img,boxCrop)
                if(result == None):
                    return None
                dst = cv.GaussianBlur(img, (3, 3), 0)
                img = dst[result[0]:result[2], result[1]:result[3]]
            img = cv.resize(img, (224,224))
            is_success, im_buf_arr = cv.imencode(".png", img)
            img_byte = im_buf_arr.tobytes()
            del img
            return img_byte
        except Exception as a:
            print(a)
            return None

    def convertImage(self,imgs : list, boxCrop : bbox = None):
        start = time.perf_counter()
        results = []
        a = len(imgs)*1.00
        b = 0.00
        imgs_path = []
        for img in imgs:
            bimg = self.imgsToBytes(img, boxCrop)
            if(bimg is not None):
                results.append(bimg)
                imgs_path.append(img)
            b+=1.00
            self.resultPublish("Convert Image",format((b/a)*100,".3f"),"{} %".format(format((b/a)*100,".3f")))
        end = time.perf_counter()
        self.resultPublish("Convert Image",0,f'Finished in {round(end-start, 2)} second(s)')
        return results,imgs_path

    def findMatchingPThee(self,imagefind,boxCrop:bbox,teach = False):
        if(self.templateMat is not None):
            self.templateMat = cv.imread(f'{self.pathMatching}/Ref3/template.png',0)
        w, h = self.templateMat.shape[::-1]
        method = eval('cv.TM_CCOEFF')
        res = cv.matchTemplate(imagefind, self.templateMat, method)
    
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)


        roi_tpleft =  (boxCrop.C1, boxCrop.R1)
        roi_bnright = (boxCrop.C2, boxCrop.R2)

        ver_offset = top_left[1]-431
        hor_offset = top_left[0]-16
        if (top_left[0] >= 14) and (top_left[0] <=25) or (top_left[0] >= 3) and (top_left[0] <=9):   # ((age>= 8) and (age<= 12))
            
            if(teach):
                os_roi_tpleft = (roi_tpleft[0]-hor_offset,roi_tpleft[1]-ver_offset)
                os_roi_bnright = (roi_bnright[0]-hor_offset, roi_bnright[1]-ver_offset)
            else:
                os_roi_tpleft = (roi_tpleft[0]+hor_offset,roi_tpleft[1]+ver_offset)
                os_roi_bnright = (roi_bnright[0]+hor_offset, roi_bnright[1]+ver_offset)
            roi:bbox = [os_roi_tpleft[1],os_roi_tpleft[0],os_roi_bnright[1],os_roi_bnright[0]]
            print(f"Mat OK {roi}")
            return roi
        else:
            print('Template Position out of Range')
            return None

    def train(self,imgs : list, boxCrop : bbox = None):
        if(imgs == None):
            self.statusPublish("Not found image !!!","ERROR")
            raise Exception("imgs is none !!!")
        if(len(imgs) == 0):
            self.statusPublish("Not found image !!!","ERROR")
            raise Exception("Don't have image !!!")
        if(len(imgs) < 20):
            self.statusPublish("Image must be > 20 !!!","ERROR")
            raise Exception("Image must be > 20")

        self.statusPublish("Initialize...","INFO")
        i_count = 0
        try:
            self.onTraining = True
            image_train = []
            train_dataset = None
            image_train,_ = self.convertImage(imgs,boxCrop)
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

    def show_pred(self,sample,fmap):
        sample_img = self.tensor_to_img(sample, True)
        fmap_img = self.pred_to_img(fmap, [0,255])*255

        pixelVal = []
        pixelVal.append(int(fmap_img[0][0] *255))
        pixelVal.append(int(fmap_img[0][1] *255))
        
        fmap_img[0][0] = 255.0000
        fmap_img[0][1] = 0.0000
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

        plt.clf()
        plt.cla()
        plt.axis('off')
        plt.imshow(fmap_img, cmap="gray", alpha=1)
        bytesImgTensor = io.BytesIO()
        fig.savefig(bytesImgTensor, format='png', bbox_inches='tight', pad_inches=0, transparent=False)
        bytesImgTensor.seek(0)
        base64ImgTensor = base64.b64encode(bytesImgTensor.read())
        strBase64Tensor = str(base64ImgTensor)[2:-1]

        plt.clf()
        plt.cla()
        plt.axis('off')
        fig.clear()
        plt.close()
        plt.close('all')
        del fig

        b64Ip = "data:image/jpg;base64,{}".format(strBase64Input)
        b64Heat = "data:image/jpg;base64,{}".format(strBase64Heat)
        b64Tensor = "data:image/png;base64,{}".format(strBase64Tensor)

        return b64Ip,b64Heat,b64Tensor,pixelVal

    def predict(self,param:InferModel):
        if(param is None):
            msg = "Argument param is None !!!"
            self.statusPublish(msg,"ERROR")
            raise Exception(msg)
        
        if(self.model is None or self.onTraining):
            msg = "not have Model in system !!!"
            self.statusPublish(msg,"ERROR")
            raise Exception(msg)

        if(param.imgList == None):
            msg = "Not found image !!!"
            self.statusPublish(msg,"ERROR")
            raise Exception(msg)

        if(len(param.imgList) == 0):
            msg = "Not found image !!!"
            self.statusPublish(msg,"ERROR")
            raise Exception(msg)


        self.statusPublish("Initialize...","INFO")
        i_count = 0

       
        image_test,imgs_path = self.convertImage(param.imgList,param.bbox)
        
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
            imgInput,imgHeat,imgTensor,picVal =  self.show_pred(sample, pxl_lvl_anom)

            if(scoreMin>255):
                scoreMin = 255
            if(scoreMax>255):
                scoreMax = 255
            
            IsReject = False
            defectPercent = 0
            imgRes = ""
            if(param.procMode == 1):
                #AnormalyMaxScore
                ams = int(param.anomalyThreshold)
                imgRes = imgHeat
                if(scoreMax > ams):
                    IsReject = True
                else:
                    IsReject = False
                pass
            elif(param.procMode == 2):
                #AnormalyRejectPosition
                positionPercen = float(param.controlValue)
                imgRes,IsReject,defectPercent = (DefectProcess()).findPixel(imgTensor,imgHeat,param.anomalyThreshold,positionPercen)
                
                pass
            else:
                #AnormalyRejectArea
                positionPercen = float(param.controlValue)
                imgRes,IsReject,defectPercent = (DefectProcess()).findDefect(imgTensor,imgHeat,param.anomalyThreshold,positionPercen)
                pass

            res = {
                "imgfilename": os.path.basename(imgs_path[n]),
                "procMode" : param.procMode,
                "scoreMin" : scoreMin,
                "scoreMax" : scoreMax,
                "defectPercent" : defectPercent,
                "isReject" : IsReject
            }
            n +=1
            self.resultPublish("Inference",0,res)
            if(param.showAllImage):
                res["resultImgInput"] = imgInput
                res["resultImgHeat"] = imgRes
            else:
                if(IsReject):
                    res["resultImgInput"] = imgInput
                    res["resultImgHeat"] = imgRes
                else:
                    res["resultImgInput"] = None
                    res["resultImgHeat"] = None
            result.append(res)
            

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