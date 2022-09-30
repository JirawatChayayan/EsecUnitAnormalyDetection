from distutils.command.config import config
from distutils.log import debug
from email.mime import image
from genericpath import isfile
from statistics import mode
from threading import Thread
from tkinter.messagebox import NO
from typing import List
from cv2 import threshold
import cv2 as cv
import numpy as np

from matplotlib.transforms import Bbox
import json
import glob
from fastapi import FastAPI,Response, status, APIRouter
from sqlalchemy import true
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from AICore.training import Training
from AICore.fileCopy import RunFileProcess, TestFileProcess,TrainingFileProcess
import time
import requests
import os
from model import TrainingModel, bbox,InferModel,MatData

training = Training()
#time.sleep(45)

inProcess = False
model = False


#AI Process
def trainingProc(imgs,bbox:bbox = None):
    global inProcess,training
    inProcess = True
    result = ""
    try:
        training.train(imgs,bbox)
        result = "finished"
    except Exception as ex:
        result = "Training_fail {}".format(ex)
    finally:
        inProcess = False
    return result

def inferenceProc(dataItem:TrainingModel):
    global inProcess,training,model
    if(inProcess):     
        return None
    try:
        if(training.model == None):
            model = False
            return None
        else:
            inProcess = True
            result = training.predict(dataItem)
            inProcess = False
            return result
    except Exception as a:
        print(a)
        pass
    finally:
        inProcess = False
    return None

#Information
def getModel():
    global inProcess,training,model
    try:
        if(training.model == None):
            model = False
        else:
            model = True
    except:
        model = False
    return model

def getOntraining():
    global training
    try:
        if(training.onTraining):
            return True
        else:
            return False
    except:
        return False


#get Info Other Service
def getConfig():
    url = "http://127.0.0.1:8084/config"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)

def getImage():
    url = "http://127.0.0.1:8082/filecontrol/images/SetupTrain"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)

def getImageTest():
    url = "http://127.0.0.1:8082/filecontrol/images/SetupTest"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)


# self test and train
def selfTraining():
    try:
        config = getConfig()
        bboxCrop = bbox()
        bboxCrop.R1 = config['bboxCrop']['R1']
        bboxCrop.C1 = config['bboxCrop']['C1']
        bboxCrop.R2 = config['bboxCrop']['R2']
        bboxCrop.C2 = config['bboxCrop']['C2']
        #print(bboxCrop)
        imgs = getImage()['imgList']
        trainingProc(imgs,bboxCrop)
    except Exception as e:
        print(e)
        pass

def selfTesting():
    try:
        config = getConfig()
        bboxCrop = config['bboxCrop']
        processMode = config['modeInspect']
        processParameter = config['processParameter']
        imgs = getImageTest()['imgList']
        
        if(imgs == None):
            return None,None,None
        if(len(imgs)==0):
            return None,None,None
        a = InferModel()
        
        a.imgList = imgs
        a.bbox = bbox()
        a.bbox.R1 = bboxCrop['R1']
        a.bbox.C1 = bboxCrop['C1']
        a.bbox.R2 = bboxCrop['R2']
        a.bbox.C2 = bboxCrop['C2']
        a.anomalyThreshold = processParameter['RejectByAMS']['Val']
        a.procMode = processMode
        if(processMode == 1):
            a.controlValue = processParameter['RejectByAMS']['Val']
        elif(processMode == 2):
            a.controlValue = processParameter['RejectByPixelPercent']['Val']
        else:
            a.controlValue = processParameter['RejectByAreaPercent']['Val']
        a.showAllImage = True
        return inferenceProc(a),a.controlValue,config['machineId']
    except Exception as a:
        print(a)
        return None,None,None

#for testing 
def getCurrentLot():
    try:
        url = "http://127.0.0.1:8085/ai_training_log/currentLot"
        response = requests.request("GET", url)
        if(response.status_code == 200):
            lotSum = json.loads(response.text)
            return lotSum #['lotNo'],lotSum['lotNoCount'],lotSum['lotNoSum']
        else:
            return None
    except:
        return None



app = FastAPI(
    title="AI Training",
    description="Load and delete file with API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

ai = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={404: {"description": "Not found"}},
)


@ai.post("/train",status_code=200)
def train(item :TrainingModel,response:Response):
    global inProcess
    t1 = time.perf_counter()
    if(inProcess):
        response.status_code = 401
        return "inProcess"
    result = trainingProc(item.imgList,item.bbox)
    if(result == "finished"):
        response.status_code = 200
        t2 = time.perf_counter()
        #delete retrain image
        training.deletefileRej()
        print(f'Finished in {round(t2-t1, 2)} second(s)')
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result

@ai.post("/infer",status_code=200)
def infer(item :InferModel,response:Response):
    global inProcess
    if(inProcess):
        response.status_code = 401
        return "inProcess"
    if(getOntraining()):
        response.status_code = 403
        return "OnTraining"
    if(getModel() == False):
        response.status_code = 405
        return "noModel"
    result = inferenceProc(item)
    if(result is not None):
        response.status_code = 200
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result


@ai.post("/getbboxoffsetpos",status_code=200)
def findmatching(item :MatData,response:Response):
    global inProcess
    if(inProcess):
        response.status_code = 401
        return "inProcess"
    img = None
    if os.path.isfile(item.img):
        img = cv.imread(item.img,0)
    elif os.path.isfile(training.pathImg+"/SetupMode/Train/"+item.img):
        img = cv.imread(training.pathImg+"/SetupMode/Train/"+item.img,0)
    elif os.path.isfile(training.pathImg+"/SetupMode/Train/"+item.img+".png"):
        img = cv.imread(training.pathImg+"/SetupMode/Train/"+item.img+".png",0)
    elif os.path.isfile(training.pathImg+"/SetupMode/Train/"+item.img+".jpg"):
        img = cv.imread(training.pathImg+"/SetupMode/Train/"+item.img+".jpg",0)
    else:
        response.status_code = 404
        return "Image Not found !!!"
    result = None
    try:
        return training.findMatchingPThee(img,item.bbox,True)
    except:
        response.status_code = 500
        return "Error to find matching"


@ai.post("/test_process",status_code=200)
def testProcess(response:Response):
    global inProcess
    if(inProcess):
        response.status_code = 401
        return "inProcess"
    lot = getCurrentLot()
    if(lot is None):
        response.status_code = 500
        return "can not connect to result data server !!!"
    
    trainingData = TrainingFileProcess()
    trainingData.processTrainImage(lot['lotNoSum'])

    testData = TestFileProcess()
    aiRes,controlVal,machineId = selfTesting()
    if(aiRes is None):
        response.status_code = 500
        return "Error to run AI"
    testData.writeData(lot,controlVal,machineId,aiRes)
    return "OK"

@ai.post("/infer_save",status_code=200)
def infer(item :InferModel,response:Response):
    global inProcess
    if(inProcess):
        response.status_code = 401
        return "inProcess"
    if(getOntraining()):
        response.status_code = 403
        return "OnTraining"
    if(getModel() == False):
        response.status_code = 405
        return "noModel"
    lot = getCurrentLot()
    if(lot is None):
        response.status_code = 500
        return "can not connect to result data server !!!"
    config = getConfig()
    bboxCrop = config['bboxCrop']
    processMode = config['modeInspect']
    processParameter = config['processParameter']
    item.bbox = bbox()
    item.bbox.R1 = bboxCrop['R1']
    item.bbox.C1 = bboxCrop['C1']
    item.bbox.R2 = bboxCrop['R2']
    item.bbox.C2 = bboxCrop['C2']

    item.anomalyThreshold = processParameter['RejectByAMS']['Val']
    item.procMode = processMode
    if(processMode == 1):
        item.controlValue = processParameter['RejectByAMS']['Val']
    elif(processMode == 2):
        item.controlValue = processParameter['RejectByPixelPercent']['Val']
    else:
        item.controlValue = processParameter['RejectByAreaPercent']['Val']
    mcId = config['machineId']
    item.showAllImage = True
    result = inferenceProc(item)
    if(result is not None):
        response.status_code = 200
        return RunFileProcess().writeData(lot,item.controlValue,mcId,result)
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result



app.include_router(ai)

@app.on_event("startup")
def startup():
    selfTraining()
    pass

@app.on_event("shutdown")
def shutdown():
    pass
    

if __name__ == '__main__':
    try:
        uvicorn.run(app, host="0.0.0.0", port=8083, log_level="info" ,debug = True)
    except KeyboardInterrupt:
        pass
        


