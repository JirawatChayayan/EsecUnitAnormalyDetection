from typing import List
from fastapi import Depends, Response, status, APIRouter,UploadFile,File
from db.table import MC_LOG
from db.db import session, get_db
from resultImage.model import ImageResultModel, GetImageModel
from sqlalchemy import and_, desc, asc
from pydantic.datetime_parse import datetime


mc_log = APIRouter(
    prefix="/stop_release_log",
    tags=["STOP RELEASE LOG RESULT"],
    responses={200: {"message": "OK"}}
)

@mc_log.post("")
async def mcLog(response:Response,remark:str,db:session = Depends(get_db)):
    try:
        table = MC_LOG()
        table.TIMESTAMP = datetime.now()
        table.REMARK = remark
        table.ACTIVEFLAG = True
        db.add(table)
        db.commit()
    except:
        response.status_code = 500

@mc_log.get("")
async def mcLog(response:Response,db:session = Depends(get_db)):
    try:
        data = db.query(MC_LOG).filter(and_(MC_LOG.ACTIVEFLAG == True)).order_by(desc(MC_LOG.TIMESTAMP)).all()

        if(data is None):
            response.status_code = 500
            return None
            
        res = []
        for a in data:
            res.append({
                'remark' : a.REMARK,
                'timestamp' : a.TIMESTAMP
            })
        return res
    except:
        response.status_code = 500

@mc_log.get("/last")
async def mcLog(response:Response,db:session = Depends(get_db)):
    try:
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