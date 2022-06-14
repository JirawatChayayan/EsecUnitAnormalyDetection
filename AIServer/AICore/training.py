
from logging import exception
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


class Training():
    def __init__(self):
        self.callbackResult = None
        self.callbackStatus = None
        self.model = None
        self.onTraining = False

    def imgsToBytes(self,imgPath :str,boxCrop : tuple = None):
        img = None
        
    
        img = cv.imread(imgPath)
        if(boxCrop is not None):
            img = img[boxCrop[0]-10:boxCrop[2]+10, boxCrop[1]-10:boxCrop[3]+10]
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

    def convertImage(self,imgs : list, boxCrop : tuple = None):
        start = time.perf_counter()
        results = []
        a = len(imgs)*1.00
        b = 0.00
        for img in imgs:
            results.append(self.imgsToBytes(img, boxCrop))
            b+=1.00
            self.resultPublish("Convert Image",format((b/a)*100,".3f"),"{} %".format(format((b/a)*100,".3f")))
        end = time.perf_counter()
        print(f'Finished in {round(end-start, 2)} second(s)')
        self.resultPublish("Convert Image",0,f'Finished in {round(end-start, 2)} second(s)')
        return results #self.byteImgS

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
                    imgInput,imgHeat = self.show_pred(sample, img_lvl_anom, pxl_lvl_anom, score)
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

    def show_pred(self,sample, score, fmap, range):
        sample_img = self.tensor_to_img(sample, normalize=True)
        fmap_img = self.pred_to_img(fmap, range)
        #cv.imwrite('color_img.jpg', fmap_img)
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
        

        
        return "data:image/jpg;base64,{}".format(strBase64Input),"data:image/jpg;base64,{}".format(strBase64Heat)


    def predict_disp(self,imgs,boxCrop : tuple = None):
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
            imgInput,imgHeat =  self.show_pred(sample, img_lvl_anom, pxl_lvl_anom, score)
            param = {
                "imgfilename": os.path.basename(imgs[n]),
                "scoreMin" : int('{:.0f}'.format(score[0])),
                "scoreMax" : int('{:.0f}'.format(score[1]))
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