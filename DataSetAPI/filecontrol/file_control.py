import shutil
import sys
import os
from filecontrol.datamodel import ImgFile, ImgMode, ImgModel, ImgCrop
import natsort
from os.path import expanduser
import cv2 as cv
import base64

class FileProcess:
    def __init__(self):
        self.initialPath()

    def createDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def initialPath(self):
        self.pathMain =  '{}/ImgScreenSave'.format(expanduser("~")) #
        self.pathSetup = '{}/SetupMode'.format(self.pathMain)
        self.pathProcess = '{}/ProcessMode'.format(self.pathMain)
        #self.pathProcess = '/home/esec-ai/ramdisk/ProcessMode'
        self.pathSetupTrain = '{}/Train'.format(self.pathSetup)
        self.pathSetupTest = '{}/Test'.format(self.pathSetup)
        self.pathReject = '{}/Reject'.format(self.pathSetup)
        self.createDir(self.pathMain)
        self.createDir(self.pathSetup)
        self.createDir(self.pathProcess)
        self.createDir(self.pathSetupTrain)
        self.createDir(self.pathSetupTest)
        self.createDir(self.pathReject)
    
    def listImgProcess(self):
        return {
            "mode" : ImgMode.Process,
            "imgList":natsort.natsorted([os.path.abspath(os.path.join(self.pathProcess, p)) for p in os.listdir(self.pathProcess)])#os.listdir(self.pathProcess)
        }

    def listImgSetupTrain(self):
        return {
            "mode" : ImgMode.SetupTrain,
            "imgList": natsort.natsorted([os.path.abspath(os.path.join(self.pathSetupTrain, p)) for p in os.listdir(self.pathSetupTrain)])#os.listdir(self.pathSetupTrain)
        }

    def listImgSetupTest(self):
        return {
            "mode" : ImgMode.SetupTest,
            "imgList" : natsort.natsorted([os.path.abspath(os.path.join(self.pathSetupTest, p)) for p in os.listdir(self.pathSetupTest)])#os.listdir(self.pathSetupTest)
        }

    def listImgReject(self):
        return {
            "mode" : ImgMode.Reject,
            "imgList" : natsort.natsorted([os.path.abspath(os.path.join(self.pathReject, p)) for p in os.listdir(self.pathReject)])
        }

    def listImg(self,imgMode : ImgMode):
        if(imgMode == ImgMode.Process):
            return self.listImgProcess()
        elif(imgMode == ImgMode.SetupTrain):
            return self.listImgSetupTrain()
        elif(imgMode == ImgMode.SetupTest):
            return self.listImgSetupTest()
        else:
            return self.listImgReject()

    def getpath(self,path :ImgMode):
        if(path == ImgMode.Process):
            return self.pathProcess
        elif(path == ImgMode.SetupTrain):
            return self.pathSetupTrain
        elif(path == ImgMode.SetupTest):
            return self.pathSetupTest
        elif(path == ImgMode.Reject):
            return self.pathReject
        else:
            return None
    
    def readImage(self,imgFile : ImgFile):
        try:
            path = imgFile.mode
            mainpath = self.getpath(path)
            if(mainpath == None):
                print('Not found Path {}'.format(path))
                return None
            strFullpath = os.path.join(mainpath,os.path.basename(imgFile.imgfilename))
            if os.path.exists(strFullpath):
                #os.remove(strFullpath)
                return strFullpath
            else:
                print("File {} does not exist".format(imgFile.imgfilename))
                return None
        except:
            return None

    def readcropImage(self,imgCrop : ImgCrop):
        try:
            path = imgCrop.mode
            bbox = imgCrop.bbox
            mainpath = self.getpath(path)
            if(mainpath == None):
                print('Not found Path {}'.format(path))
                return None
            strFullpath = os.path.join(mainpath,os.path.basename(imgCrop.imgfilename))
            if os.path.exists(strFullpath):
                #os.remove(strFullpath)
                img = cv.imread(strFullpath)
                if(bbox is not None):
                    img = img[bbox[0]:bbox[2], bbox[1]:bbox[3]]
                    imgb64 = self.convertImg(img,'.jpeg')
                    # img = cv.resize(img, (224,224))
                    del img
                return imgb64
            else:
                print("File {} does not exist".format(imgCrop.imgfilename))
                return None
        except:
            return None
    
    def convertImg(self,img,format = '.png'):
        _, buffer = cv.imencode(format, img)
        png_as_text = str(base64.b64encode(buffer))[2:-1]
        imgType = 'png'
        if(format == '.png'):
            imgType = 'png'
        else:
            imgType = 'jpeg'
        res = "data:image/{};base64,{}".format(imgType,png_as_text)

        return res

    def deleteImgList(self,imgDetail: ImgModel):
        try:
            path = imgDetail.mode
            mainpath = self.getpath(path)
            if(mainpath == None):
                print('Not found Path {}'.format(path))
                return  
            for f in imgDetail.imgList:
                try:
                    strFullpath = os.path.join(mainpath,f)
                    if os.path.exists(strFullpath):
                        os.remove(strFullpath)
                    else:
                        print("File {} does not exist".format(f))
                except Exception as e:
                    print('Error delete file {}'.format(f))
        except:
            pass   

    def getFullpath(self,imgDetail: ImgModel):
        listImg = []
        path = imgDetail.mode
        mainpath = self.getpath(path)
        if(mainpath == None):
            print('Not found Path {}'.format(path))
            raise ValueError('Not found Path {}'.format(path))
        for f in imgDetail.imgList:
            try:
                strFullpath = os.path.join(mainpath,f)
                if os.path.exists(strFullpath):
                    #os.remove(strFullpath)
                    listImg.append(strFullpath)
                else:
                    print("File {} does not exist".format(f))
            except Exception as e:
                print('Error load file {}'.format(f))
        return listImg

    def moveImgReject(self,imgDetail: ImgModel):
        try:
            path = imgDetail.mode
            mainpath = self.getpath(path)
            secpath = self.getpath("SetupTrain")
            if(mainpath == None):
                print('Not found Path {}'.format(path))
                return  
            for f in imgDetail.imgList:
                try:
                    fn = os.path.basename(f)
                    rejectPath = os.path.join(mainpath,fn)
                    movePath = os.path.join(secpath, fn)
                    if os.path.exists(rejectPath):
                        shutil.move(rejectPath, movePath)
                    else:
                        print("File {} does not exist".format(fn))
                except Exception as e:
                    print('Error Move file {}'.format(fn))
        except:
            pass

if __name__ == '__main__':
    file = FileProcess()
    print(file.listImgProcess())
