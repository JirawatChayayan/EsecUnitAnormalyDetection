from typing import List
from urllib import response
from fastapi import Depends, Response, status, APIRouter,UploadFile,File
from db.table import ALL_RESULT
from db.db import session, get_db
from resultAll.model import ImageResultAllModel, GetImageModel,GetAnomalyInfo
from sqlalchemy import and_, desc, asc,func,text
from pydantic.datetime_parse import datetime
import threading 
import schedule
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import base64
import io
import cv2 as cv
import os 


all_result = APIRouter(
    prefix="/all_result",
    tags=["ALL RESULT"],
    responses={200: {"message": "OK"}}
)



def imgnotFound():
    return 'data:image/jpeg;base64,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'

def plotGraph(unitRange,data1,data2,caption1,caption2,graph_title,x_label,y_label):
    df = pd.DataFrame({
        "data1" : data1,
        "data2" : data2,
        "range" : unitRange
    })
    fig = plt.figure(figsize=(10,5))
    plt.plot(df.range, df.data1, label=caption1,color = 'royalblue', linewidth=2)
    plt.plot(df.range, df.data2, label=caption2,color = 'crimson', linewidth=2)

    plt.title(graph_title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.tight_layout()
    bytesImgInput = io.BytesIO()
    fig.savefig(bytesImgInput, format='jpg', bbox_inches='tight', pad_inches=0, transparent=False)
    bytesImgInput.seek(0)
    base64ImgInput = base64.b64encode(bytesImgInput.read())
    strBase64Img = str(base64ImgInput)[2:-1]
    #plt.show()
    plt.cla()
    plt.clf()
    plt.close()
    plt.close('all')
    del fig

    return  "data:image/jpg;base64,{}".format(strBase64Img)

def plot(datas,lotSum):
    if(datas is None):
        raise Exception('Get data error !!!')
    proc1Data = datas['procMode1']
    proc2Data = datas['procMode2']
    proc3Data = datas['procMode3']


    res = {
        'procMode1' : None,
        'procMode2' : None,
        'procMode3' : None
    }

    if(proc1Data is not None):
        #plotdata ams
        # allUnit = proc1Data['unitCount'][-1]
        rejectUnit = 0
        i = 0
        allUnit = 0
        for a in proc1Data['scoreMax']:
            allUnit +=1
            if(a > proc1Data['setupValue'][i]):
                rejectUnit += 1
            i+=1
        res['procMode1'] = plotGraph(proc1Data['unitCount'],
                  proc1Data['scoreMax'],
                  proc1Data['setupValue'],
                  'unit_anomaly_score',
                  'reject_threshold_value',
                  f'Anormaly max score Lot {lotSum} summary {allUnit} unit reject {rejectUnit} unit.',                  
                  "Number of unit run",
                  "Anormaly score")

    if(proc2Data is not None):
        #plotdata ams
        allUnit = 0#proc2Data['unitCount'][-1]
        rejectUnit = 0
        i = 0
        for a in proc2Data['defectPercent']:
            allUnit += 1
            if(a > proc2Data['setupValue'][i]):
                rejectUnit += 1
            i+=1
        res['procMode2'] = plotGraph(proc2Data['unitCount'],
                proc2Data['defectPercent'],
                proc2Data['setupValue'],
                'unit_anomaly_percent',
                'reject_anomaly_percent',
                f'Unit anomaly Lot {lotSum} summary {allUnit} unit reject {rejectUnit} unit.',                  
                "Number of unit run",
                "Anormaly percent")

    if(proc3Data is not None):
        #plotdata ams
        allUnit = 0#proc3Data['unitCount'][-1]
        rejectUnit = 0
        i = 0
        for a in proc3Data['defectPercent']:
            allUnit +=1
            if(a > proc3Data['setupValue'][i]):
                rejectUnit += 1
            i+=1
        res['procMode3'] = plotGraph(proc3Data['unitCount'],
                proc3Data['defectPercent'],
                proc3Data['setupValue'],
                'unit_anomaly_area_percent',
                'reject_anomaly_area_percent',
                f'Unit anomaly Lot {lotSum} summary {allUnit} unit reject {rejectUnit} unit.',                  
                "Number of unit run",
                "Anormaly area percent")

    return res

def cvimg2base64(img):
    _,buffer = cv.imencode('.jpg',img)
    jpg_as_txt = base64.b64encode(buffer)
    return "data:image/jpg;base64,{}".format(str(jpg_as_txt)[2:-1])

def paintlabel(img,isReject = True):
    #rectangle
    start_point = (0, 0)
    end_point = None
    color = None
    if(isReject):
        color = (0, 0, 255)
        end_point = (55, 20)
    else:
        color = (0,207,21)
        end_point = (47, 20)
    thickness = -1
    image = cv.rectangle(img, start_point, end_point, color, thickness)

    #text
    font = cv.FONT_HERSHEY_SIMPLEX
    org = (3, 15)
    fontScale = 0.5

    color = None
    txt = ""
    if(isReject):
        color = (255, 255, 255)
        txt = 'Reject'
    else:
        color = (0, 0, 0)
        txt = 'Good'
    thickness = 1
    image = cv.putText(image, txt, org, font, fontScale, color, thickness, cv.LINE_AA)
    
    return cvimg2base64(image)

def getTop5Anomaly(db,dataItem:GetAnomalyInfo,procMode):
    dataProc = None
    if(procMode == 1):
        dataProc  = db.query(ALL_RESULT) \
                                .where(ALL_RESULT.ACTIVEFLAG == True,
                                        ALL_RESULT.LOT_NO == dataItem.lotNo,
                                        ALL_RESULT.LOT_NO_COUNT == dataItem.lotNoCount,
                                        ALL_RESULT.PROCESS_MODE == procMode) \
                                .order_by(desc(ALL_RESULT.SCORE_MAX)).limit(5).all()
    else:
        dataProc = db.query(ALL_RESULT) \
                        .where(ALL_RESULT.ACTIVEFLAG == True,
                                ALL_RESULT.LOT_NO == dataItem.lotNo,
                                ALL_RESULT.LOT_NO_COUNT == dataItem.lotNoCount,
                                ALL_RESULT.PROCESS_MODE == procMode) \
                        .order_by(desc(ALL_RESULT.DEFECT_PERCENT)).limit(5).all()
    
    if(dataProc is None):
        return None
    else:
        res = []
        for a in dataProc:
            imgHeatPath = a.IMG_HEATMAP_PATH
            if(os.path.isfile(imgHeatPath)):
                img = cv.imread(imgHeatPath)
                res.append({
                    "img" : paintlabel(img,a.IS_REJECT),
                    "scoremax" : a.SCORE_MAX,
                    "defectPercent" : a.DEFECT_PERCENT
                })
            else:
                res.append({
                    "img" : imgnotFound(),
                    "scoremax" : a.SCORE_MAX,
                    "defectPercent" : a.DEFECT_PERCENT
                })

        lendata = len(res)
        if(lendata < 5):
            for i in range(lendata,5):
                res.append({
                    "img" : imgnotFound(),
                    "scoremax" : 0,
                    "defectPercent" : 0.0
                })
        return res

def getTimeSeriesData(db,dataItem:GetAnomalyInfo):
    data : ALL_RESULT = db.query(ALL_RESULT) \
                    .where(ALL_RESULT.ACTIVEFLAG == True,
                            ALL_RESULT.LOT_NO == dataItem.lotNo,
                            ALL_RESULT.LOT_NO_COUNT == dataItem.lotNoCount) \
                    .order_by(asc(ALL_RESULT.CREATEDATE)).all()
    if(data is None):
        return None
    if(len(data)== 0):
        return None 

    scoreMax = []
    defectPercent = []
    setupValue = []
    datetime = []
    filename = []
    
    res = {
        "procMode1":{
            "unitCount":[],
            "scoreMax":[],
            "defectPercent":[],
            "setupValue":[],
            "datetime":[],
            "filename":[]
        },
        "procMode2":{
            "unitCount":[],
            "scoreMax":[],
            "defectPercent":[],
            "setupValue":[],
            "datetime":[],
            "filename":[]
        },
        "procMode3":{
            "unitCount":[],
            "scoreMax":[],
            "defectPercent":[],
            "setupValue":[],
            "datetime":[],
            "filename":[]
        }
    }
    i1 = 1
    i2 = 1
    i3 = 1
    for a in data:
        if(a.PROCESS_MODE == 1):
            res["procMode1"]["unitCount"].append(i1)
            res["procMode1"]["scoreMax"].append(a.SCORE_MAX)
            res["procMode1"]["defectPercent"].append(a.DEFECT_PERCENT)
            res["procMode1"]["setupValue"].append(a.SETUP_VALUE)
            res["procMode1"]["datetime"].append(a.CREATEDATE)
            res["procMode1"]["filename"].append(a.FILENAME)
            i1+=1
            
        elif(a.PROCESS_MODE == 2):
            res["procMode2"]["unitCount"].append(i2)
            res["procMode2"]["scoreMax"].append(a.SCORE_MAX)
            res["procMode2"]["defectPercent"].append(a.DEFECT_PERCENT)
            res["procMode2"]["setupValue"].append(a.SETUP_VALUE)
            res["procMode2"]["datetime"].append(a.CREATEDATE)
            res["procMode2"]["filename"].append(a.FILENAME)
            i2+=1
        else:
            res["procMode3"]["unitCount"].append(i3)
            res["procMode3"]["scoreMax"].append(a.SCORE_MAX)
            res["procMode3"]["defectPercent"].append(a.DEFECT_PERCENT)
            res["procMode3"]["setupValue"].append(a.SETUP_VALUE)
            res["procMode3"]["datetime"].append(a.CREATEDATE)
            res["procMode3"]["filename"].append(a.FILENAME)
            i3+=1

    if(len(res["procMode1"]["unitCount"]) == 0):
        res["procMode1"] = None
    
    if(len(res["procMode2"]["unitCount"]) == 0):
        res["procMode2"] = None
    
    if(len(res["procMode3"]["unitCount"]) == 0):
        res["procMode3"] = None

    return res



# run result API

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

@all_result.get("/lotlist",status_code=200)
def getlotList(response:Response, db:session = Depends(get_db)):
    data = db.query(ALL_RESULT.LOT_NO,ALL_RESULT.LOT_NO_COUNT).distinct()
    if(data is None):
        response.status_code = 404
        return
    res = {}
    for a in data:
        key = a['LOT_NO']
        if(key not in res):
            res[key] = []
            res[key].append(a['LOT_NO_COUNT']) 
        else:
            res[key].append(a['LOT_NO_COUNT']) 
    #response.body = res

    return res

@all_result.post("/lotAnomalyInfo",status_code=200)
def getInfo(dataItem:GetAnomalyInfo,response:Response, db:session = Depends(get_db)):
    res = getTimeSeriesData(db,dataItem)
    if(res is None):
        response.status_code = 404
        return None
    return res

@all_result.post("/lotAnomalyInfoGraph",status_code=200)
def getInfo(dataItem:GetAnomalyInfo,response:Response, db:session = Depends(get_db)):
    res = getTimeSeriesData(db,dataItem)
    if(res is None):
        response.status_code = 404
        return None
    return plot(res,f'{dataItem.lotNo}_{dataItem.lotNoCount}')

@all_result.post("/gettop5imganormaly",status_code=200)
def gettop5(dataItem:GetAnomalyInfo,response:Response, db:session = Depends(get_db)):

    img1 = getTop5Anomaly(db,dataItem,1)
    img2 = getTop5Anomaly(db,dataItem,2)
    img3 = getTop5Anomaly(db,dataItem,3)

    res = {
        "top5Proc1" : img1,
        "top5Proc2" : img2,
        "top5Proc3" : img3,
    }
    return res

@all_result.post("/getlistofimgRun/{processMode}",status_code=200)
def getofimgrun_inlot(dataItem : GetAnomalyInfo,processMode:int,response:Response, db:session = Depends(get_db)):
    resDb = db.query(ALL_RESULT.FILENAME).where(ALL_RESULT.ACTIVEFLAG == True,
                                    ALL_RESULT.LOT_NO == dataItem.lotNo,
                                    ALL_RESULT.LOT_NO_COUNT == dataItem.lotNoCount,
                                    ALL_RESULT.PROCESS_MODE == processMode).all()
    if(resDb is None):
        response.status_code = 404
        return None
    res = []
    for a in resDb:
        res.append(a['FILENAME'])
    return res

@all_result.get("/image/{fileName}/{processMode}",status_code=200)
def getImage(filename:str,processMode:int,response:Response, db:session = Depends(get_db)):
    resDb = db.query(ALL_RESULT).where(ALL_RESULT.ACTIVEFLAG == True,
                                       ALL_RESULT.FILENAME == filename,
                                       ALL_RESULT.PROCESS_MODE == processMode).first()

    if(resDb is None):
        response.status_code = 404
        return None
    pathImgRaw = resDb.IMG_RAW_PATH
    pathImgHeat = resDb.IMG_HEATMAP_PATH

    scoremax = resDb.SCORE_MAX
    defectpercent = resDb.DEFECT_PERCENT
    setupVal = resDb.SETUP_VALUE
    procMode = resDb.PROCESS_MODE
    lotno = resDb.LOT_NO
    lotnocount = resDb.LOT_NO_COUNT
    isReject = resDb.IS_REJECT
    createDate = resDb.CREATEDATE

    b64ImgRaw = None
    b64ImgResult = None
    if(os.path.isfile(pathImgRaw)):
        img = cv.imread(pathImgRaw,cv.IMREAD_GRAYSCALE)
        b64ImgRaw = cvimg2base64(img)
        del img
    else:
        b64ImgRaw = imgnotFound()
    
    if(os.path.isfile(pathImgHeat)):
        img = cv.imread(pathImgRaw,cv.IMREAD_COLOR)
        b64ImgResult = cvimg2base64(img)
        del img
    else:
        b64ImgResult = imgnotFound()

    return {
        "imgRaw" : b64ImgRaw,
        "imgHeat" : b64ImgResult,
        "ams" : scoremax,
        "defectPercent" : defectpercent,
        "setupValue" : setupVal,
        "isReject" : isReject,
        "procMode" : procMode,
        "lotNo" :lotno,
        "lotNoCount" : lotnocount,
        "createDate" : createDate, 
    }
    
@all_result.post("/call_summary_unit_result/{processMode}",status_code=200)
def get_unit_summary(dataItem:GetAnomalyInfo,processMode :int,response:Response, db:session = Depends(get_db)):
    if(dataItem is None):
        response.status_code = 500
        return None
    resQuery = db.query(ALL_RESULT.IS_REJECT).where(ALL_RESULT.ACTIVEFLAG == True,
                                                    ALL_RESULT.LOT_NO == dataItem.lotNo,
                                                    ALL_RESULT.LOT_NO_COUNT == dataItem.lotNoCount,
                                                    ALL_RESULT.PROCESS_MODE == processMode).all()
    if(resQuery is None):
        response.status_code = 404
        return None

    if(len(resQuery) == 0):
        response.status_code = 404
        return None

    unitALL = 0
    rejectUnit = 0
    for a in resQuery:
        unitALL += 1
        res = a['IS_REJECT']
        if(res):
            rejectUnit += 1
    goodUnit = unitALL - rejectUnit

    return {
        "unitAll" : unitALL,
        "rejectUnit" : rejectUnit,
        "goodUnit" : goodUnit
    }
    


# @all_result.post("/getlistofimgRun",status_code=200)
# def getofimgrun_inlot2(dataItem : GetAnomalyInfo,response:Response, db:session = Depends(get_db)):
#     resDb = db.query(ALL_RESULT.FILENAME).where(ALL_RESULT.ACTIVEFLAG == True,
#                                     ALL_RESULT.LOT_NO == dataItem.lotNo,
#                                     ALL_RESULT.LOT_NO_COUNT == dataItem.lotNoCount).all()
#     if(resDb is None):
#         response.status_code = 404
#         return None
#     res = []
#     for a in resDb:
#         res.append(a['FILENAME'])
#     return res
    

# @all_result.get("/image/{fileName}",status_code=200)
# def getImage2(filename:str,response:Response, db:session = Depends(get_db)):    # resDb = db.query(ALL_RESULT).where(ALL_RESULT.ACTIVEFLAG == True,
    #                                    ALL_RESULT.FILENAME == filename).first()

    # if(resDb is None):
    #     response.status_code = 404
    #     return None

    # pathImgRaw = resDb.IMG_RAW_PATH
    # pathImgHeat = resDb.IMG_HEATMAP_PATH

    # scoremax = resDb.SCORE_MAX
    # defectpercent = resDb.DEFECT_PERCENT
    # setupVal = resDb.SETUP_VALUE
    # procMode = resDb.PROCESS_MODE
    # lotno = resDb.LOT_NO
    # lotnocount = resDb.LOT_NO_COUNT
    # isReject = resDb.IS_REJECT
    # createDate = resDb.CREATEDATE

    # b64ImgRaw = None
    # b64ImgResult = None
    # if(os.path.isfile(pathImgRaw)):
    #     img = cv.imread(pathImgRaw,cv.IMREAD_GRAYSCALE)
    #     b64ImgRaw = cvimg2base64(img)
    #     del img
    # else:
    #     b64ImgRaw = imgnotFound()
    
    # if(os.path.isfile(pathImgHeat)):
    #     img = cv.imread(pathImgRaw,cv.IMREAD_COLOR)
    #     b64ImgResult = cvimg2base64(img)
    #     del img
    # else:
    #     b64ImgResult = imgnotFound()

    # return {
    #     "imgRaw" : b64ImgRaw,
    #     "imgHeat" : b64ImgResult,
    #     "ams" : scoremax,
    #     "defectPercent" : defectpercent,
    #     "setupValue" : setupVal,
    #     "isReject" : isReject,
    #     "procMode" : procMode,
    #     "lotNo" :lotno,
    #     "lotNoCount" : lotnocount,
    #     "createDate" : createDate, 
    # }
    # resDb = db.query(ALL_RESULT).where(ALL_RESULT.ACTIVEFLAG == True,
    #                                    ALL_RESULT.FILENAME == filename).first()

    # if(resDb is None):
    #     response.status_code = 404
    #     return None

    # pathImgRaw = resDb.IMG_RAW_PATH
    # pathImgHeat = resDb.IMG_HEATMAP_PATH

    # scoremax = resDb.SCORE_MAX
    # defectpercent = resDb.DEFECT_PERCENT
    # setupVal = resDb.SETUP_VALUE
    # procMode = resDb.PROCESS_MODE
    # lotno = resDb.LOT_NO
    # lotnocount = resDb.LOT_NO_COUNT
    # isReject = resDb.IS_REJECT
    # createDate = resDb.CREATEDATE

    # b64ImgRaw = None
    # b64ImgResult = None
    # if(os.path.isfile(pathImgRaw)):
    #     img = cv.imread(pathImgRaw,cv.IMREAD_GRAYSCALE)
    #     b64ImgRaw = cvimg2base64(img)
    #     del img
    # else:
    #     b64ImgRaw = imgnotFound()
    
    # if(os.path.isfile(pathImgHeat)):
    #     img = cv.imread(pathImgRaw,cv.IMREAD_COLOR)
    #     b64ImgResult = cvimg2base64(img)
    #     del img
    # else:
    #     b64ImgResult = imgnotFound()

    # return {
    #     "imgRaw" : b64ImgRaw,
    #     "imgHeat" : b64ImgResult,
    #     "ams" : scoremax,
    #     "defectPercent" : defectpercent,
    #     "setupValue" : setupVal,
    #     "isReject" : isReject,
    #     "procMode" : procMode,
    #     "lotNo" :lotno,
    #     "lotNoCount" : lotnocount,
    #     "createDate" : createDate, 
    # }