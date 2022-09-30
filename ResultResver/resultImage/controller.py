from typing import List
from fastapi import Depends, Response, status, APIRouter,UploadFile,File
from db.table import REJECT_RESULT
from db.db import session, get_db
from resultImage.model import ImageResultModel, GetImageModel
from sqlalchemy import and_, desc, asc
from pydantic.datetime_parse import datetime
import threading 
import schedule
import time

lock = threading.Lock()
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
    print('clear cache start reject_result')
    lock.acquire()
    if(dataCache is not None):
        dataCache.clear()
        dataCache = None
    lock.release()
    print('clear cache finish reject_result')
    
def insertData(db):
    global dataCache,lock
    lock.acquire()
    aaa = dataCache
    lock.release()
    if(aaa is not None):
        return aaa

    datas = db.query(REJECT_RESULT.LOT_NO,\
                     REJECT_RESULT.LOT_NO_COUNT,\
                     REJECT_RESULT.FILENAME,\
                     REJECT_RESULT.SCORE_MIN,\
                     REJECT_RESULT.SCORE_MAX,\
                     REJECT_RESULT.DEFECT_PERCENT,\
                     REJECT_RESULT.SETUP_VALUE,\
                     REJECT_RESULT.PROCESS_MODE,\
                     REJECT_RESULT.MACHINE_NO,\
                     REJECT_RESULT.CREATEDATE)\
                     .filter(and_(REJECT_RESULT.ACTIVEFLAG == True)).order_by(desc(REJECT_RESULT.CREATEDATE)).all()
    if(datas is None):
        return None
    
    lock.acquire()
    data = []
    dataCache = []

    for a in datas:
        obj = {
            'lotNo': a['LOT_NO'],
            'lotNoCount': a['LOT_NO_COUNT'],
            'imgFileName': a['FILENAME'],

            'scoreMin': a['SCORE_MIN'],
            'scoreMax': a['SCORE_MAX'],
            'defectPercent': a['DEFECT_PERCENT'],

            'setupValue': a['SETUP_VALUE'],
            'processMode': a['PROCESS_MODE'],
            'machineNo': a['MACHINE_NO'],
            'createDate': a['CREATEDATE']
        }
        data.append(obj)
        dataCache.append(obj)
    lock.release()
    return data


schedule.every(1800).seconds.do(background_job)
stop_run_continuously = None

result_reject = APIRouter(
    prefix="/reject_result",
    tags=["REJECT RESULT"],
    responses={200: {"message": "OK"}}
)

def detect_image_type(base64_data):
    extensions = {
        "data:image/png;": "png",
        "data:image/jpeg;": "jpg",
        "data:image/jpg;": "jpg",
    }
    for ext in extensions:
        if base64_data.startswith(ext):
            return True
    return False

def splitImgdata(strImage):
    if(not detect_image_type(strImage)):
        raise Exception("Image format not correct.")
    datasplit = strImage.split(',')
    if(len(datasplit) != 2):
        raise Exception("Image format not correct.")
    imgType = datasplit[0].strip()
    imgBase64Str = datasplit[1].strip()
    # imgBinary = base64.b64decode(imgBase64Str)
    return imgType,imgBase64Str

@result_reject.post("")
def postdata(response:Response,result:List[ImageResultModel], db:session = Depends(get_db)):
    global dataCache,lock
    for data in result:
        try:
            imgRaw_Type,imgRaw_Binary = splitImgdata(data.imgRaw)
            imgHeat_Type,imgHeat_Binary = splitImgdata(data.imgHeatMap)
            #typeSome = '{},{}'.format(imgRaw_Type,imgHeat_Type)
            #print(imgHeat_Binary)
            table = REJECT_RESULT()

            table.LOT_NO = data.lotNo.strip()
            table.LOT_NO_COUNT = data.lotNoCount
            table.FILENAME = data.imgFileName

            table.IMG_RAW = data.imgRaw
            table.IMG_HEATMAP = data.imgHeatMap

            table.SCORE_MIN = data.scoreMin
            table.SCORE_MAX = data.scoreMax

            table.DEFECT_PERCENT = data.defectPercent
            table.SETUP_VALUE = data.setupValue
            table.PROCESS_MODE = data.processMode
            table.MACHINE_NO = data.machineNo

            time = datetime.now()
            table.CREATEDATE = time
            db.add(table)
            db.commit()
            lock.acquire()
            aaa = dataCache
            lock.release()
            if(aaa is None):
                insertData(db)
            else:
                lock.acquire()
                dataCache.insert(0,{
                    'lotNo': data.lotNo.strip(),
                    'lotNoCount': data.lotNoCount,
                    'imgFileName': data.imgFileName,

                    'scoreMin': data.scoreMin,
                    'scoreMax': data.scoreMax,
                    'defectPercent': data.defectPercent,

                    'setupValue': data.setupValue,
                    'processMode': data.processMode,
                    'machineNo': data.machineNo, 
                    'createDate': time
                })
                lock.release()
        except Exception as ex:
            response.status_code = 500
            return {'msg': ex}
    return {'msg':'Created'}

@result_reject.get("image/{imgFileName}")
def getImg(response:Response,imgFileName:str,db:session = Depends(get_db)):
    data = db.query(REJECT_RESULT.IMG_RAW,REJECT_RESULT.IMG_HEATMAP).filter(and_(REJECT_RESULT.ACTIVEFLAG == True,REJECT_RESULT.FILENAME == imgFileName)).first()
    if(data is None):
        response.status_code = 404
        return {'msg':'No image id := {}'.format(id)}
    
    return {
        'imgRaw': data['IMG_RAW'],
        'imgHeatMap': data['IMG_HEATMAP']
    }

@result_reject.get("")
def getImg(response:Response,db:session = Depends(get_db)):
    aaa = insertData(db)
    if(aaa is None):
        response.status_code = 404
    return aaa

@result_reject.on_event("startup")
def startup():
    global stop_run_continuously
    # Start the background thread
    stop_run_continuously = run_continuously(100)
    pass

@result_reject.on_event("shutdown")
def shutdown():
    global stop_run_continuously
    # Stop the background thread
    stop_run_continuously.set()
    pass
