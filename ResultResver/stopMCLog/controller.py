from typing import List
from fastapi import Depends, Response, status, APIRouter,UploadFile,File
from db.table import MC_LOG
from db.db import session, get_db
from resultImage.model import ImageResultModel, GetImageModel
from sqlalchemy import and_, desc, asc
from pydantic.datetime_parse import datetime

import threading 
import schedule
import time
lock = threading.Lock()

mc_log = APIRouter(
    prefix="/stop_release_log",
    tags=["STOP RELEASE LOG RESULT"],
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
    print('clear cache start stop_release_log')
    lock.acquire()
    if(dataCache is not None):
        dataCache.clear()
        dataCache = None
    lock.release()
    print('clear cache finish stop_release_log')
    


schedule.every(1800).seconds.do(background_job)
stop_run_continuously = None



@mc_log.post("")
async def mcLog(response:Response,remark:str,db:session = Depends(get_db)):
    global dataCache,lock
    lock.acquire()
    try:
        table = MC_LOG()
        table.TIMESTAMP = datetime.now()
        table.REMARK = remark
        table.ACTIVEFLAG = True
        db.add(table)
        db.commit()
        
        if(dataCache is None):
            #initial Cache
            data = db.query(MC_LOG).filter(and_(MC_LOG.ACTIVEFLAG == True)).order_by(desc(MC_LOG.TIMESTAMP)).all()
            if(data is None):
                dataCache = None
            dataCache = []
            for a in data:
                dataCache.append({
                    'remark' : a.REMARK,
                    'timestamp' : a.TIMESTAMP
                })
                
        else:
            dataCache.insert(0,{
                'remark' : table.REMARK,
                'timestamp' : table.TIMESTAMP
            })
    except:
        response.status_code = 500
    lock.release()

@mc_log.get("")
async def mcLog(response:Response,db:session = Depends(get_db)):
    global dataCache,lock
    try:

        lock.acquire()
        aaa = dataCache
        lock.release()
        if(aaa is not None):
            return aaa
        data = db.query(MC_LOG).filter(and_(MC_LOG.ACTIVEFLAG == True)).order_by(desc(MC_LOG.TIMESTAMP)).all()

        if(data is None):
            response.status_code = 500
            return None
        lock.acquire()
        res = []
        dataCache = []
        for a in data:
            obj = {
                'remark' : a.REMARK,
                'timestamp' : a.TIMESTAMP
            }
            res.append(obj)
            dataCache.append(obj)
        lock.release()
        return res
    except:
        response.status_code = 500

@mc_log.get("/last")
async def mcLog(response:Response,db:session = Depends(get_db)):
    global dataCache,lock
    try:
        lock.acquire()
        aaa = dataCache
        lock.release()
        if(aaa is not None):
            return aaa[0]
        a = db.query(MC_LOG).filter(and_(MC_LOG.ACTIVEFLAG == True)).order_by(desc(MC_LOG.TIMESTAMP)).first()

        if(a is None):
            response.status_code = 500
            return None
        return {
                'remark' : a.REMARK,
                'timestamp' : a.TIMESTAMP
            }
    except:
        response.status_code = 500


@mc_log.on_event("startup")
def startup():
    global stop_run_continuously
    # Start the background thread
    stop_run_continuously = run_continuously(100)
    pass

@mc_log.on_event("shutdown")
def shutdown():
    global stop_run_continuously
    # Stop the background thread
    stop_run_continuously.set()
    pass