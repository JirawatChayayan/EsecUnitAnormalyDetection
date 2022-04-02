from ast import Str
from distutils.command.config import config
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

lock = threading.Lock()

class ConfigModel(BaseModel):
    machineId : str = 'ESEC2008-01P'
    rejectThreshold:int = 120
    stopWhenRejectCount:int = 1
    changeModeWhenProcessTrigCount:int = 20 
    useAI:bool = False
    inferenceRate:int = 5
    bboxCrop:list = [690,490,915,712]

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
        conf.machineId = dataItem.machineId
        conf.changeModeWhenProcessTrigCount = dataItem.changeModeWhenProcessTrigCount
        conf.rejectThreshold = dataItem.rejectThreshold
        conf.stopWhenRejectCount = dataItem.stopWhenRejectCount
        conf.useAI = dataItem.useAI
        conf.inferenceRate = dataItem.inferenceRate
        conf.saveconfig()
        res = True
    except:
        res = False
    finally:
        lock.release()
    if(res == False):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return res

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
    pass

@app.on_event("shutdown")
def shutdown():
    pass

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8084, log_level="info")
    except KeyboardInterrupt:
        pass
