import json
from os import PRIO_PGRP
from typing import List
from fastapi import Depends, Response, status, APIRouter,UploadFile,File
from db.table import AITrainingLog
from db.db import session, get_db
from  AITrainingLog.model import  AITrainingLogModel
from sqlalchemy import and_, desc, asc
from pydantic.datetime_parse import datetime
import threading 

import schedule
import time

lock = threading.Lock()



logAI = APIRouter(
    prefix="/ai_training_log",
    tags=["AI TRAINING LOG"],
    responses={200: {"message": "OK"}}
)


dataCache = None

def run_continuously(interval=1):
    cease_continuous_run = threading.Event()
    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)
    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

def background_job():
    global lock,dataCache
    print('clear cache start ai_training_log')
    lock.acquire()
    if(dataCache is not None):
        dataCache.clear()
        dataCache = None
    lock.release()
    print('clear cache finish ai_training_log')
    


schedule.every(1800).seconds.do(background_job)
stop_run_continuously = None

def inputcachedata(db):
    global dataCache,lock
    lock.acquire()
    aaa = dataCache
    lock.release()
    if(aaa is not None):
        return aaa
    data = db.query(AITrainingLog).order_by(desc(AITrainingLog.TRAINING_FINISH)).all()
    res = []
    if data is None:
        return None
    lock.acquire()
    try:
        dataCache = []
        for a in data:
            obj = {
                    "userTraining": a.TRAINER,
                    "userLevel": a.TRAINER_LEVEL,
                    "lotNo" : a.LOT_NO,
                    "lotNoCount" : a.LOT_NO_COUNT,
                    "nImgTrain" : a.TRAINING_IMAGE,
                    "roiCropImg": json.loads(a.TRAINING_ROI),
                    "startTrain": a.TRAINING_START,
                    "finishTrain": a.TRAINING_FINISH,
                    "remark": a.REMARK
                }
            res.append(obj)
            dataCache.append(obj)
    except:
        res = None
        dataCache = None
        pass
    lock.release()
    return res


@logAI.post("")
def postdata(response:Response,logAI: AITrainingLogModel, db:session = Depends(get_db)):
    global dataCache,lock
    try:
        if(logAI == None):
            response.status_code = 400
            return "No input data"
        lotNo = logAI.lotNo.strip()
        if(lotNo == ""):
            response.status_code = 400
            return "No lot data"

        print(logAI.startTrain)
        print(logAI.finishTrain)
        print(logAI.userTraining)
        print(logAI.userLevel)
        print(logAI.nImgTrain)
        print(logAI.remark)
        print(logAI.lotNo)
        print(logAI.roiCropImg)

        getOldData = db.query(AITrainingLog.LOT_NO,AITrainingLog.LOT_NO_COUNT,AITrainingLog.TRAINING_FINISH).filter(AITrainingLog.LOT_NO == lotNo).order_by(desc(AITrainingLog.LOT_NO_COUNT)).first()

        print(getOldData)
        lot_no_count = 1
        if(getOldData == None):
            lot_no_count = 1
        else:
            lot_no_count = getOldData['LOT_NO_COUNT']+1
        
        print(lot_no_count)

        tb = AITrainingLog()
        tb.TRAINER = str(logAI.userTraining.strip())
        tb.LOT_NO = lotNo
        tb.LOT_NO_COUNT = lot_no_count
        tb.TRAINER_LEVEL = str(logAI.userLevel.strip())
        tb.TRAINING_IMAGE = int(logAI.nImgTrain)
        tb.TRAINING_ROI = json.dumps(
            {
                "R1":logAI.roiCropImg.R1,
                "C1":logAI.roiCropImg.C1,
                "R2":logAI.roiCropImg.R2,
                "C2":logAI.roiCropImg.C2
            }
        )
        tb.TRAINING_START = logAI.startTrain
        tb.TRAINING_FINISH = logAI.finishTrain
        if(logAI.remark is not None):
            tb.REMARK = str(logAI.remark)
        db.add(tb)
        db.commit() 
        
        if(dataCache is None):
            #initial cache
            inputcachedata(db)
        else:
            lock.acquire()
            dataCache.insert(0,{
                "userTraining": tb.TRAINER,
                "userLevel": tb.TRAINER_LEVEL,
                "lotNo" : tb.LOT_NO,
                "lotNoCount" : tb.LOT_NO_COUNT,
                "nImgTrain" : tb.TRAINING_IMAGE,
                "roiCropImg": json.loads(tb.TRAINING_ROI),
                "startTrain": tb.TRAINING_START,
                "finishTrain": tb.TRAINING_FINISH,
                "remark": tb.REMARK
            })
            lock.release()
    except Exception as ex:
        print(ex)
        response.status_code = 500
        return {'msg': ex}
    aaa = inputcachedata(db)[0]
    return {
        "lotNo": aaa['lotNo'],
        "lotNoCount" : aaa['lotNoCount'],
        "lotNoSum":"{}_{}".format(aaa['lotNo'],aaa['lotNoCount'])
    }

@logAI.get("")
def getdata(response:Response,db:session = Depends(get_db)):
    global dataCache,lock
    aaa = inputcachedata(db)
    if(aaa is not None):
        return aaa
    else:
        response.status_code = 404
        return {'msg':'No data.'}

@logAI.get("/currentLot")
def getcurrentLot(response:Response,db:session = Depends(get_db)):
    global lock,dataCache
    aaa = inputcachedata(db)[0]
    return {
        "lotNo": aaa['lotNo'],
        "lotNoCount" : aaa['lotNoCount'],
        "lotNoSum":"{}_{}".format(aaa['lotNo'],aaa['lotNoCount'])
    }



@logAI.on_event("startup")
def startup():
    global stop_run_continuously
    # Start the background thread
    stop_run_continuously = run_continuously(100)
    pass

@logAI.on_event("shutdown")
def shutdown():
    global stop_run_continuously
    # Stop the background thread
    stop_run_continuously.set()
    lock.release()
    pass