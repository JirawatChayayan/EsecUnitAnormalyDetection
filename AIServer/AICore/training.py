
from PIL import Image
import io
from torch.utils.data import DataLoader
import torch
from AICore.data import StreamingDataset,IMAGENET_MEAN, IMAGENET_STD
from AICore.models import SPADE
import glob
import os
import time
from os.path import expanduser


class Training():
    def __init__(self):
        self.callbackResult = None
        self.callbackStatus = None
        self.model = None

    def imgsToBytes(self,imgPath :str,boxCrop : tuple = None):
        img = None
        im = Image.open(imgPath)
        if(boxCrop == None):
            img = im
        else:
            img = im.crop(boxCrop)
            #img.save('{}/{}.png'.format('/home/esec-ai/Crop_RGB',i_count))
            #(img.convert('L')).save('{}/{}.png'.format('/home/esec-ai/Crop_Gray',i_count))
        buf = io.BytesIO()
        img.resize((224,224))
        img.save(buf, format='PNG')
        img_byte = buf.getvalue()
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
            self.model = SPADE(k=50,backbone_name="wide_resnet50_2",)
            self.model.callbackResult = self.resultPublish
            self.model.fit(DataLoader(train_dataset))
            #torch.save(self.model, self.weightFileName())

            #self.predict(imgs[1],boxCrop)

            self.resultPublish("Training",100,"Finished.")
            self.statusPublish("Start Finished.","INFO")
        else:
            self.statusPublish("Can not training this image !!!","ERROR")
    
    def predict(self,imgs,boxCrop : tuple = None):
        if(self.model is None):
            self.statusPublish("not have Model in system  !!!","ERROR")
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
            img_lvl_norm,pixel_lvl_norm = self.model.predict(sample.unsqueeze(0))
            score = pixel_lvl_norm.min(),pixel_lvl_norm.max()
            param = {
                "imgfilename": os.path.basename(imgs[n]),
                "scoreMin" : int('{:.0f}'.format(score[0])),
                "scoreMax" : int('{:.0f}'.format(score[1]))
            }
            n +=1
            result.append(param)
            self.resultPublish("Inference",0,param)
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