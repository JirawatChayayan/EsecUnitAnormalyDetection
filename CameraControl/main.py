from typing import Optional
from fastapi import FastAPI, APIRouter
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from proc.processcamera import ProcessCamera
from proc.serialConnect import ModeRun
import sys
import os





procCam = ProcessCamera()

app = FastAPI(
    title="SYSTEM CONFIG",
    description="EDIT CONFIC SYSTEM BELOW",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

camRouter = APIRouter(
    prefix="/camcontrol",
    tags=["camcontrol"],
    responses={404: {"description": "Not found"}},
)

# @camRouter.get("/getmode/")
# def get_mode():
#     procCam.mqtt.sendModeChange(procCam.trig.modeRun)
#     return {
#         "modeRun" : procCam.trig.modeRun,
#         "isRunning": procCam.trig.serialHandle.is_open and procCam.cam.camConnected
#     }
# @camRouter.get("/setmode/{mode}")
# def get_mode(mode : int):
#     if(mode == 2):
#         procCam.trig.sendSerial(ModeRun.Process)
#     else:
#         procCam.trig.sendSerial(ModeRun.Setup)
#     procCam.mqtt.sendModeChange(procCam.trig.modeRun)
#     return {
#         "modeRun" : procCam.trig.modeRun,
#         "isRunning": procCam.trig.serialHandle.is_open and procCam.cam.camConnected
#     }
@camRouter.get("/saveImageTrain")
def get_train():
    if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
        procCam.saveThisImageAPITrain = True
        return True
    return False

@camRouter.get("/saveImageTest")
def get_test():
    if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
        procCam.saveThisImageAPITest = True
        return True
    return False

@camRouter.get("/saveImageProc")
def get_test():
    if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
        procCam.saveThisImageProc = True
        return True
    return False


@camRouter.on_event("startup")
def startup():
    procCam.connect()

@camRouter.on_event("shutdown")
def shutdown():
    procCam.stopped.set()
    procCam.disconnect()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

app.include_router(camRouter)

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info")
    except KeyboardInterrupt:
        pass

