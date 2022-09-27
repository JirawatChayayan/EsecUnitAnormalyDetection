from ast import Str
from distutils.command.config import config
from distutils.log import debug
from tokenize import String
from typing import List, Optional
from fastapi import FastAPI,Response, status, APIRouter
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pyexpat import model
from pydantic import BaseModel
from config import AIConfig
import threading
from model import ConfigModel, bbox,controlParameter,controlParameterInt,processParameter


lock = threading.Lock()


app = FastAPI(
    title="Config Files",
    description="Config",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

@app.get("/")
async def redirect_typer():
    return RedirectResponse("http://0.0.0.0:8084/docs")

con = APIRouter(
    prefix="/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)

@con.post("",status_code=200)
def update_config(dataItem: ConfigModel,response:Response):
    res = False
    lock.acquire()
    try:
        conf = AIConfig()
        conf.setnewConfig2(dataItem)
        res = True
    except:
        res = False
    finally:
        lock.release()
    if(res == False):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return res

@con.post("/roi",status_code=200)
def update_config(bbox: bbox,response:Response):
    res = False
    lock.acquire()
    try:
        if(bbox is not None):
            res = AIConfig().setnewbbox(bbox)
    except:
        res = False
    finally:
        lock.release()
    if(res == False):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return res

@con.get("/mode",status_code=200)
def getMode(response:Response):
    return AIConfig().modeInspectDetail




##################### AMS #####################

@con.post("/set_rejectAMS_val",status_code=200)
def update_AMS(val: int,response:Response):
    res = False
    lock.acquire()
    try:
        if(val is not None):
            res = AIConfig().setRejectByAMS(val)
    except:
        res = False
    finally:
        lock.release()
    if(res == False):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return res

@con.post("/set_rejectAMS_param",status_code=200)
def update_AMS_param(param: controlParameterInt,response:Response):
    res = False
    lock.acquire()
    try:
        if(param is not None):
            res = AIConfig().setRejectByAMSParam(param)
    except:
        res = False
    finally:
        lock.release()
    if(res == False):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return res

@con.get("/rejectAMS_param",status_code=200)
def get_ams_param():
    return AIConfig().getRejectByAMSParam()

################ pixel percent ###############
@con.post("/set_reject_pixel_percent_val",status_code=200)
def update_pixPercent(val: float,response:Response):
    res = False
    lock.acquire()
    try:
        if(val is not None):
            res = AIConfig().setRejectByPixelPercent(val)
    except:
        res = False
    finally:
        lock.release()
    if(res == False):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return res

@con.post("/set_reject_pixel_percent_param",status_code=200)
def update_pixPercentParam(val: controlParameter,response:Response):
    res = False
    lock.acquire()
    try:
        if(val is not None):
            res = AIConfig().setRejectByPixelPercentParam(val)
    except:
        res = False
    finally:
        lock.release()
    if(res == False):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return res

@con.get("/reject_pixel_percent_param",status_code=200)
def get_pixPrecent_param():
    return AIConfig().getRejectByPixelPercentParam()


################ area percent ###############
@con.post("/set_reject_area_percent_val",status_code=200)
def update_areaPercent(val: float,response:Response):
    res = False
    lock.acquire()
    try:
        if(val is not None):
            res = AIConfig().setRejectByAreaPercent(val)
    except:
        res = False
    finally:
        lock.release()
    if(res == False):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return res

@con.post("/set_reject_area_percent_param",status_code=200)
def update_areaPercentParam(val: controlParameter,response:Response):
    res = False
    lock.acquire()
    try:
        if(val is not None):
            res = AIConfig().setRejectByAreaPercentParam(val)
    except:
        res = False
    finally:
        lock.release()
    if(res == False):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return res

@con.get("/reject_area_percent_param",status_code=200)
def get_area_percent_param():
    return AIConfig().getRejectByAreaPercentParam()


@con.get("",status_code=200)
def get_config(response:Response):
    lock.acquire()
    data = None
    try:
        data = AIConfig().getCurrentConfig()
    except:
        data = None
    finally:
        lock.release()
    if(data == None):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return data

app.include_router(con)

@app.on_event("startup")
def startup():
    AIConfig().getCurrentConfig()
    pass

@app.on_event("shutdown")
def shutdown():
    pass

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8084, log_level="info",debug = True)
    except KeyboardInterrupt:
        pass
