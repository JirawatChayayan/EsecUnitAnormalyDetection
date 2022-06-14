import json
from typing import List
from fastapi import Depends, Response, status, APIRouter,UploadFile,File
from db.table import AITrainingLog
from db.db import session, get_db
from  AITrainingLog.model import  AITrainingLogModel
from sqlalchemy import and_, desc, asc
from pydantic.datetime_parse import datetime

logAI = APIRouter(
    prefix="/ai_training_log",
    tags=["AI TRAINING LOG"],
    responses={200: {"message": "OK"}}
)


@logAI.post("")
async def postdata(response:Response,logAI: AITrainingLogModel, db:session = Depends(get_db)):
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
    except Exception as ex:
        response.status_code = 500
        return {'msg': ex}
    return {'msg':'Created'}


@logAI.get("")
async def getdata(response:Response,db:session = Depends(get_db)):
    data = db.query(AITrainingLog).order_by(desc(AITrainingLog.TRAINING_FINISH)).all()
    res = []
    if data is None:
        response.status_code = 404
        return {'msg':'No data.'}
    for a in data:
        res.append({
        "userTraining": a.TRAINER,
        "userLevel": a.TRAINER_LEVEL,
        "nImgTrain" : a.TRAINING_IMAGE,
        "roiCropImg": json.loads(a.TRAINING_ROI),
        "startTrain": a.TRAINING_START,
        "finishTrain": a.TRAINING_FINISH,
        "remark": a.REMARK
    })
    return res