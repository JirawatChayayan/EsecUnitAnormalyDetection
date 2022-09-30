from typing import List
from fastapi import Depends, Response, status, APIRouter,UploadFile,File
from db.table import ALL_RESULT
from db.db import session, get_db
from resultAll.model import ImageResultAllModel, GetImageModel
from sqlalchemy import and_, desc, asc
from pydantic.datetime_parse import datetime
import threading 
import schedule
import time
from datetime import datetime


all_result = APIRouter(
    prefix="/all_result",
    tags=["ALL RESULT"],
    responses={200: {"message": "OK"}}
)


@all_result.post("",status_code=200)
def saveData(response:Response,results:List[ImageResultAllModel], db:session = Depends(get_db)):
    if(results is None):
        response.status_code = 400
        return None
    for res in results:
        try:
            unixtime = float((res.imgFileName.split('.')[0]).replace('_','.'))
            table = ALL_RESULT()
            table.LOT_NO = res.lotNo
            table.LOT_NO_COUNT = res.lotNoCount
            table.FILENAME = res.imgFileName

            table.IMG_RAW_PATH = res.imgRawPath
            table.IMG_HEATMAP_PATH = res.imgHeatMapPath

            table.SCORE_MIN = res.scoreMin
            table.SCORE_MAX = res.scoreMax

            table.DEFECT_PERCENT = res.defectPercent
            table.SETUP_VALUE = res.setupValue
            table.PROCESS_MODE = res.processMode
            table.IS_REJECT = res.isReject

            table.MACHINE_NO = res.machineNo
            table.CREATEDATE = datetime.fromtimestamp(unixtime)
            
            db.add(table)
            db.commit()
        except:
            pass
    return "OK"