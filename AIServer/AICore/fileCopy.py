from asyncore import write
import csv
import shutil
import glob
import natsort
import os
from datetime import datetime
from typing import List
import cv2 as cv
import base64
import numpy as np

import requests
import json


class SaveAllResultAsFile:
    def __init__(self):
        self.initialPath()

    def createDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def initialPath(self):
        self.pathMain =  '{}/AnormalyResultAll'.format(os.path.expanduser("~")) #
        self.pathImage = '{}/Image'.format(self.pathMain)
        self.pathCSV = '{}/CSV'.format(self.pathMain)

        self.pathCSVRun = '{}/CSV-Run'.format(self.pathCSV)
        self.pathCSVTest = '{}/CSV-Test'.format(self.pathCSV)
        self.pathCSVTrain = '{}/CSV-Train'.format(self.pathCSV)

        self.pathImgRun = '{}/ImageRun'.format(self.pathImage)
        self.pathImgTest = '{}/ImageTest'.format(self.pathImage)
        self.pathImgTrain = '{}/ImageTrain'.format(self.pathImage)

        self.createDir(self.pathMain)
        self.createDir(self.pathImage)
        self.createDir(self.pathCSV)

        self.createDir(self.pathCSVRun)
        self.createDir(self.pathCSVTest)
        self.createDir(self.pathCSVTrain)

        self.createDir(self.pathImgRun)
        self.createDir(self.pathImgTest)
        self.createDir(self.pathImgTrain)

    def imgHeatPath(self,path):
        a = '{}/ImgHeat'.format(path)
        self.createDir(a)
        return a
    
    def imgInputPath(self,path):
        a = '{}/ImgInput'.format(path)
        self.createDir(a)
        return a
    
    def detect_image_type(self,base64_data):
        extensions = {
            "data:image/png;": "png",
            "data:image/jpeg;": "jpg",
            "data:image/jpg;": "jpg",
        }
        for ext in extensions:
            if base64_data.startswith(ext):
                return True
        return False

    def splitImgdata(self,strImage):
        if(not self.detect_image_type(strImage)):
            raise Exception("Image format not correct.")
        datasplit = strImage.split(',')
        if(len(datasplit) != 2):
            raise Exception("Image format not correct.")
        imgType = datasplit[0].strip()
        imgBase64Str = datasplit[1].strip()
        # imgBinary = base64.b64decode(imgBase64Str)
        return imgType,imgBase64Str

    def b64toImg(self,b64,resize = False):
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
        imgResize = cv.resize(img,(200,200))
        return imgResize
    
class TrainingFileProcess:
    def __init__(self):
        self.initialPath()

    def createDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def initialPath(self):
        self.pathMain =  '{}/AnormalyResultAll'.format(os.path.expanduser("~")) #
        self.pathFolderTrain = '{}/ImgScreenSave/SetupMode/Train'.format(os.path.expanduser('~'))
        self.pathImage = '{}/Image'.format(self.pathMain)
        self.pathCSV = '{}/CSV'.format(self.pathMain)
        self.pathCSVTrain = '{}/CSV-Train'.format(self.pathCSV)
        self.pathImgTrain = '{}/ImageTrain'.format(self.pathImage)

        self.createDir(self.pathMain)
        self.createDir(self.pathImage)
        self.createDir(self.pathCSV)
        self.createDir(self.pathCSVTrain)
        self.createDir(self.pathImgTrain)
        self.createDir(self.pathFolderTrain)

    def writeCSVTrain(self,lotNo,fileList):
        csvPath = os.path.join(self.pathCSVTrain,f"{lotNo.strip()}.csv")
        fHandle = None 
        writer = None
        if(os.path.exists(csvPath) == False):
            fHandle = open(csvPath, 'w',newline='')
            writer = csv.writer(fHandle)
            row = ["FileNameList"]
            writer.writerow(row)
        else:
            fHandle = open(csvPath, 'a')
            writer = csv.writer(fHandle)
            now = datetime.now()
            date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
            row = [""]
            writer.writerow(row)
            row = [f"Append On {date_time_str}"]
            writer.writerow(row)

        for a in fileList:
            row = [a]
            writer.writerow(row)

        if(fHandle is not None):
            fHandle.close()
    
    def copyFileIfNotExit(self,src,dest):
        imgsPath = natsort.natsorted([os.path.abspath(os.path.join(src, p)) for p in os.listdir(src)])
        imgsfile = []
        for imgFile in imgsPath:
            fName = os.path.basename(imgFile)
            destFilePath = os.path.join(dest,fName)

            if(os.path.exists(destFilePath) == False):
                try:
                    shutil.copyfile(imgFile, destFilePath)
                    print(f"File Copies {fName}")
                    imgsfile.append(fName)
                except:
                    print(f"File notfound {fName}")
            else:
                print(f"Have {fName} file in destination path.")
                imgsfile.append(fName)
        return imgsfile

    def processTrainImage(self,lotNo):
        imgCopy = self.copyFileIfNotExit(self.pathFolderTrain,self.pathImgTrain)
        self.writeCSVTrain(lotNo,imgCopy)

class TestFileProcess:
    def __init__(self):
        self.initialPath()

    def createDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def initialPath(self):
        self.pathMain =  '{}/AnormalyResultAll'.format(os.path.expanduser("~")) #
        self.pathImage = '{}/Image'.format(self.pathMain)
        self.pathCSV = '{}/CSV'.format(self.pathMain)
        self.pathCSVTest = '{}/CSV-Test'.format(self.pathCSV)
        self.pathImgTest = '{}/ImageTest'.format(self.pathImage)

        self.createDir(self.pathMain)
        self.createDir(self.pathImage)
        self.createDir(self.pathCSV)
        self.createDir(self.pathCSVTest)
        self.createDir(self.pathImgTest)

    def imgHeatPath(self,lotno):
        a = '{}/{}/ImgHeat'.format(self.pathImgTest,lotno)
        self.createDir(a)
        return a
    
    def imgInputPath(self,lotno):
        a = '{}/{}/ImgInput'.format(self.pathImgTest,lotno)
        self.createDir(a)
        return a
    
    def detect_image_type(self,base64_data):
        extensions = {
            "data:image/png;": "png",
            "data:image/jpeg;": "jpg",
            "data:image/jpg;": "jpg",
        }
        for ext in extensions:
            if base64_data.startswith(ext):
                return True
        return False

    def splitImgdata(self,strImage):
        if(not self.detect_image_type(strImage)):
            raise Exception("Image format not correct.")
        datasplit = strImage.split(',')
        if(len(datasplit) != 2):
            raise Exception("Image format not correct.")
        imgType = datasplit[0].strip()
        imgBase64Str = datasplit[1].strip()
        # imgBinary = base64.b64decode(imgBase64Str)
        return imgType,imgBase64Str

    def b64toImg(self,b64,resize = False):
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
        imgResize = cv.resize(img,(200,200))
        return imgResize
    
    def writeData(self,lotData,controlValue,machineNo,resultDict = []):
        #['lotNo'],lotSum['lotNoCount'],lotSum['lotNoSum']
        lotsum = lotData['lotNoSum'].strip()
        csvPath = os.path.join(self.pathCSVTest,f"{lotsum.strip()}.csv")
        fHandle = None 
        writer = None

        if(os.path.exists(csvPath) == False):
            fHandle = open(csvPath, 'w',newline='')
            writer = csv.writer(fHandle)
            row = ["imgfilename","scoreMin","scoreMax","procMode","defectPercent","isReject","lotNo","lotNoCount","setupValue","imgPathInput","imgPathHeat","machineNo"]
            writer.writerow(row)
        else:
            fHandle = open(csvPath, 'a')
            writer = csv.writer(fHandle)
            now = datetime.now()
            date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
            row = ["","","","","","","","","","","",""]
            writer.writerow(row)
            row = [f"Append On {date_time_str}","","","","","","","","","","",""]
            writer.writerow(row)

        for res in resultDict:
            try:
                strFname = res['imgfilename'].split('.')[0]+".jpg"
                imgRawPath = os.path.join(self.imgInputPath(lotsum),strFname)
                imgHeatPath = os.path.join(self.imgHeatPath(lotsum),strFname)
                imgRaw = self.b64toImg(res['resultImgInput'])
                imgHeat = self.b64toImg(res['resultImgHeat'])
                cv.imwrite(imgRawPath,imgRaw)
                cv.imwrite(imgHeatPath,imgHeat)
                row = [res['imgfilename'],res['scoreMin'],res['scoreMax'],res['procMode'],res['defectPercent'],str(res['isReject']),lotData['lotNo'],lotData['lotNoCount'],controlValue,imgRawPath,imgHeatPath,machineNo]
                writer.writerow(row)
            except:
                pass

        fHandle.close()
        pass

class RunFileProcess:
    def __init__(self):
        self.initialPath()

    def createDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def initialPath(self):
        self.pathMain =  '{}/AnormalyResultAll'.format(os.path.expanduser("~")) #
        self.pathImage = '{}/Image'.format(self.pathMain)
        self.pathCSV = '{}/CSV'.format(self.pathMain)
        self.pathCSVTest = '{}/CSV-Run'.format(self.pathCSV)
        self.pathImgTest = '{}/ImageRun'.format(self.pathImage)

        self.createDir(self.pathMain)
        self.createDir(self.pathImage)
        self.createDir(self.pathCSV)
        self.createDir(self.pathCSVTest)
        self.createDir(self.pathImgTest)

    def imgHeatPath(self,lotno):
        a = '{}/{}/ImgHeat'.format(self.pathImgTest,lotno)
        self.createDir(a)
        return a
    
    def imgInputPath(self,lotno):
        a = '{}/{}/ImgInput'.format(self.pathImgTest,lotno)
        self.createDir(a)
        return a
    
    def detect_image_type(self,base64_data):
        extensions = {
            "data:image/png;": "png",
            "data:image/jpeg;": "jpg",
            "data:image/jpg;": "jpg",
        }
        for ext in extensions:
            if base64_data.startswith(ext):
                return True
        return False

    def splitImgdata(self,strImage):
        if(not self.detect_image_type(strImage)):
            raise Exception("Image format not correct.")
        datasplit = strImage.split(',')
        if(len(datasplit) != 2):
            raise Exception("Image format not correct.")
        imgType = datasplit[0].strip()
        imgBase64Str = datasplit[1].strip()
        # imgBinary = base64.b64decode(imgBase64Str)
        return imgType,imgBase64Str

    def b64toImg(self,b64,resize = False):
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
        imgResize = cv.resize(img,(200,200))
        return imgResize
    

    def savetoDB(self,res):
        try:
            url = "http://127.0.0.1:8085/all_result"
            payload = json.dumps(res)
            headers = { 
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
        except:
            pass


    def writeData(self,lotData,controlValue,machineNo,resultDict = []):
        #['lotNo'],lotSum['lotNoCount'],lotSum['lotNoSum']
        lotsum = lotData['lotNoSum'].strip()
        csvPath = os.path.join(self.pathCSVTest,f"{lotsum.strip()}.csv")
        fHandle = None 
        writer = None

        if(os.path.exists(csvPath) == False):
            fHandle = open(csvPath, 'w',newline='')
            writer = csv.writer(fHandle)
            row = ["imgfilename","scoreMin","scoreMax","procMode","defectPercent","isReject","lotNo","lotNoCount","setupValue","imgPathInput","imgPathHeat","machineNo"]
            writer.writerow(row)
        else:
            fHandle = open(csvPath, 'a')
            writer = csv.writer(fHandle)

        resultforDB = []
        resultforReturn = []
        for res in resultDict:
            try:
                strFname = res['imgfilename'].split('.')[0]+".jpg"
                imgRawPath = os.path.join(self.imgInputPath(lotsum),strFname)
                imgHeatPath = os.path.join(self.imgHeatPath(lotsum),strFname)
                imgRaw = self.b64toImg(res['resultImgInput'])
                imgHeat = self.b64toImg(res['resultImgHeat'])
                cv.imwrite(imgRawPath,imgRaw)
                cv.imwrite(imgHeatPath,imgHeat)
                row = [res['imgfilename'],res['scoreMin'],res['scoreMax'],res['procMode'],res['defectPercent'],str(res['isReject']),lotData['lotNo'].strip(),lotData['lotNoCount'],controlValue,imgRawPath,imgHeatPath,machineNo]
                writer.writerow(row)

                objdb = {
                    "lotNo":lotData['lotNo'].strip(),
                    "lotNoCount":lotData['lotNoCount'],
                    "imgRawPath":imgRawPath,
                    "imgHeatMapPath":imgHeatPath,
                    "scoreMin": res['scoreMin'],
                    "scoreMax": res['scoreMax'],

                    "defectPercent": res['defectPercent'],
                    "setupValue" : controlValue,
                    "processMode" : res['procMode'],
                    "isReject": res['isReject'],

                    "machineNo": machineNo,
                    "imgFileName": res['imgfilename']
                }
                resultforDB.append(objdb)

                
                imgHeatb64 = ""
                imgRawb64 = ""
                if(res['isReject']):
                    imgHeatb64 = res['resultImgHeat']
                    imgRawb64 = res['resultImgInput']


                objRetResult = {
                    "lotNo":lotData['lotNo'].strip(),
                    "lotNoCount":lotData['lotNoCount'],
                    "imgRaw": imgRawb64,
                    "imgHeatMap": imgHeatb64,
                    "scoreMin": res['scoreMin'],
                    "scoreMax": res['scoreMax'],
                    "defectPercent": res['defectPercent'],
                    "setupValue" : controlValue,
                    "processMode" : res['procMode'],
                    "machineNo": machineNo,
                    "imgFileName": res['imgfilename']
                }
                resultforReturn.append(objRetResult)
            except:
                pass
        fHandle.close()
        self.savetoDB(resultforDB)
        return resultforReturn
