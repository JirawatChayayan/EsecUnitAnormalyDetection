import json
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




@logAI.post("")
async def postdata(response:Response,logAI: AITrainingLogModel, db:session = Depends(get_db)):
    global dataCache,lock
    try:
        print(logAI.startTrain)
        print(logAI.finishTrain)
        print(logAI.userTraining)
        print(logAI.userLevel)
        print(logAI.nImgTrain)
        print(logAI.remark)
        print(str(logAI.roiCropImg))
        tb = AITrainingLog()
        tb.TRAINER = str(logAI.userTraining.strip())
        tb.TRAINER_LEVEL = str(logAI.userLevel.strip())
        tb.TRAINING_IMAGE = int(logAI.nImgTrain)
        tb.TRAINING_ROI = json.dumps(logAI.roiCropImg)
        tb.TRAINING_START = logAI.startTrain
        tb.TRAINING_FINISH = logAI.finishTrain
        if(logAI.remark is not None):
            tb.REMARK = str(logAI.remark)
        db.add(tb)
        db.commit() 
        lock.acquire()
        if(dataCache is None):
            #initial cache
            dataCache = []
            data = db.query(AITrainingLog).order_by(desc(AITrainingLog.TRAINING_FINISH)).all()
            if data is None:
                dataCache = None
            for a in data:
                dataCache.append({
                    "userTraining": a.TRAINER,
                    "userLevel": a.TRAINER_LEVEL,
                    "nImgTrain" : a.TRAINING_IMAGE,
                    "roiCropImg": json.loads(a.TRAINING_ROI),
                    "startTrain": a.TRAINING_START,
                    "finishTrain": a.TRAINING_FINISH,
                    "remark": a.REMARK
                })
                print(a)
        else:
            dataCache.insert(0,{
                "userTraining": tb.TRAINER,
                "userLevel": tb.TRAINER_LEVEL,
                "nImgTrain" : tb.TRAINING_IMAGE,
                "roiCropImg": json.loads(tb.TRAINING_ROI),
                "startTrain": tb.TRAINING_START,
                "finishTrain": tb.TRAINING_FINISH,
                "remark": tb.REMARK
            })
        lock.release()
    except Exception as ex:
        response.status_code = 500
        try:
            lock.release()
        except:
            pass
        return {'msg': ex}
    return {'msg':'Created'}


@logAI.get("")
async def getdata(response:Response,db:session = Depends(get_db)):
    global dataCache,lock

    lock.acquire()
    aaa = dataCache
    lock.release()
    if(aaa is not None):
        return aaa
    data = db.query(AITrainingLog).order_by(desc(AITrainingLog.TRAINING_FINISH)).all()
    res = []
    if data is None:
        response.status_code = 404
        return {'msg':'No data.'}

    lock.acquire()
    dataCache = []
    for a in data:
        obj = {
                "userTraining": a.TRAINER,
                "userLevel": a.TRAINER_LEVEL,
                "nImgTrain" : a.TRAINING_IMAGE,
                "roiCropImg": json.loads(a.TRAINING_ROI),
                "startTrain": a.TRAINING_START,
                "finishTrain": a.TRAINING_FINISH,
                "remark": a.REMARK
            }
        res.append(obj)
        dataCache.append(obj)
    lock.release()
    return res

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
    pass