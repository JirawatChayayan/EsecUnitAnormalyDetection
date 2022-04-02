from typing import List, Optional
from fastapi import FastAPI,Response, status, APIRouter
import uvicorn
from starlette.middleware.cors import CORSMiddleware
import sys
import os
from filecontrol.datamodel import ImgMode,ImgModel
from filecontrol.file_control import FileProcess
import threading 
from fastapi.responses import RedirectResponse

lock = threading.Lock()

app = FastAPI(
    title="DataSet Files",
    description="Load and delete file with API",
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
    return RedirectResponse("http://0.0.0.0:8082/docs")


fileControl = APIRouter(
    prefix="/filecontrol",
    tags=["filecontrol"],
    responses={404: {"description": "Not found"}},
)

@fileControl.get("/images/{imgMode}",status_code=200)
def get_image(imgMode: ImgMode,response:Response):
    res = None
    lock.acquire()
    try:
        res = FileProcess().listImg(imgMode)
    except Exception as ex:
        print(ex)
        res = None
    lock.release()
    if(res == None):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return res

@fileControl.delete("/images/",status_code=200)
def get_image(dataItem: ImgModel,response:Response):
    res = False
    lock.acquire()
    try:
        FileProcess().deleteImgList(dataItem)
        res = True
    except:
        res = False
    lock.release()
    if(res == False):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return res

app.include_router(fileControl)

@app.on_event("startup")
def startup():
    pass

@app.on_event("shutdown")
def shutdown():
    pass
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8082, log_level="info")
    except KeyboardInterrupt:
        pass
