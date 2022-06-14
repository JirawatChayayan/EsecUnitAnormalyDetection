from typing import List
from fastapi import Depends, Response, status, APIRouter,UploadFile,File
from db.table import REJECT_RESULT
from db.db import session, get_db
from resultImage.model import ImageResultModel, GetImageModel
from sqlalchemy import and_, desc, asc
from pydantic.datetime_parse import datetime


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
async def postdata(response:Response,result:List[ImageResultModel], db:session = Depends(get_db)):
    for data in result:
        try:
            imgRaw_Type,imgRaw_Binary = splitImgdata(data.imgRaw)
            imgHeat_Type,imgHeat_Binary = splitImgdata(data.imgHeatMap)
            #typeSome = '{},{}'.format(imgRaw_Type,imgHeat_Type)
            #print(imgHeat_Binary)
            table = REJECT_RESULT()
            table.IMG_RAW = data.imgRaw
            table.IMG_HEATMAP = data.imgHeatMap
            table.SCORE_MIN = data.scoreMin
            table.SCORE_MAX = data.scoreMax
            table.MACHINE_NO = data.machineNo
            table.FILENAME = data.imgFileName
            table.REJECT_THRESHOLD = data.rejectThreshold 
            table.CREATEDATE = datetime.now()
            db.add(table)
            db.commit()

        except Exception as ex:
            response.status_code = 500
            return {'msg': ex}
    return {'msg':'Created'}

@result_reject.get("image/{imgFileName}")
async def getImg(response:Response,imgFileName:str,db:session = Depends(get_db)):
    data = db.query(REJECT_RESULT.IMG_RAW,REJECT_RESULT.IMG_HEATMAP).filter(and_(REJECT_RESULT.ACTIVEFLAG == True,REJECT_RESULT.FILENAME == imgFileName)).first()
    if(data is None):
        response.status_code = 404
        return {'msg':'No image id := {}'.format(id)}
    
    return {
        'imgRaw': data['IMG_RAW'],
        'imgHeatMap': data['IMG_HEATMAP']
    }

@result_reject.get("")
async def getImg(response:Response,db:session = Depends(get_db)):
    datas = db.query(REJECT_RESULT.FILENAME,REJECT_RESULT.SCORE_MIN,REJECT_RESULT.SCORE_MAX,REJECT_RESULT.REJECT_THRESHOLD,REJECT_RESULT.CREATEDATE).filter(and_(REJECT_RESULT.ACTIVEFLAG == True)).order_by(desc(REJECT_RESULT.CREATEDATE)).all()
    if(datas is None):
        response.status_code = 500
        return None
    
    data = []
    for a in datas:
        data.append({
        'imgFileName': a['FILENAME'],
        'scoreMin': a['SCORE_MIN'],
        'scoreMax': a['SCORE_MAX'],
        'rejectThreshold': a['REJECT_THRESHOLD'],
        'createDate': a['CREATEDATE']
    })

    return data
