from concurrent.futures import thread
import json
from typing import Optional
from fastapi import FastAPI, APIRouter, Response
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from proc.processcamera import ProcessCamera
from proc.serialConnect import ModeRun
import sys
import os
from proc.getip import GetIPAddress
import time
import requests

time.sleep(50)
procCam = ProcessCamera()

app = FastAPI(
    title="Camera And IO Control",
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

def saveLog(msg):
    url = "http://0.0.0.0:8085/stop_release_log?remark={}".format(msg.strip())
    try:
        response = requests.request("POST", url,timeout=3)
        print(response.text)
    except:
        pass

def getLastState():
    url = "http://127.0.0.1:8085/stop_release_log/last"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    obj = json.loads(response.text)
    msg = obj['remark']
    firstWord = msg.split()[0]
    return firstWord == "Stop"



is_stopMachine = False

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

@camRouter.get("/setDispConfig/{mcID}")
def setDisp(mcID:str):
    #return True
    if(mcID == None or mcID == "" or mcID == str('{mcid}')):
        return False
    if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
        procCam.trig.sendInformation(mcID)
        return True
    return False

@camRouter.get("/is_stopMachine/",status_code=200)
def setDisp(response :Response):
    if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
        return procCam.trig.lastStateStopMC
    response.status_code = 500
    return False

@camRouter.get("/stopMC/{stop}")
def stopMC(stop :bool):
    if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
        procCam.trig.sendStopMachine(stop)

        is_stopMachine = stop
        state = "release"
        if(stop):
            state = "stop"
        msgres = "Machine is {} by manual.".format(state)
        saveLog(msgres)
        procCam.trig.sendStopMachine(stop)
        return True
    return False

@camRouter.get("/stopMC/{stop}/msg/{msg}")
def stopMC_msg(stop :bool,msg: str):
    if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
        procCam.trig.sendStopMachine(stop)
        saveLog(msg)
        procCam.trig.sendStopMachine(stop)
        return True
    return False


@camRouter.get("/AllOutput/{on}")
def allOutput(on :bool):
    if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
        procCam.trig.AllIO(on)
        return True
    return False


@camRouter.get("/setOutput/{ch}")
def setOutput(ch :int):
    if(ch >7 and ch < 1):
        return False
    if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
        procCam.trig.setIO(ch)
        return True
    return False

@camRouter.get("/resetOutput/{ch}")
def resetOutput(ch: int):
    if(ch >7 and ch < 1):
        return False
    if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
        procCam.trig.resetIO(ch)
        return True
    return False

@camRouter.on_event("startup")
def startup():
    try:
        print('Reset usb')
        # os.popen("sudo modprobe -r usbhid && sleep 5 && sudo modprobe usbhid",'w').write("esec-ai\n")
        # time.sleep(20)
        print('Reset usb OK')
    except:
        print('Reset usb Error')
        pass

    isStop = print(getLastState())
    procCam.connect()
    procCam.trig.sendStopMachine(isStop)
    # if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
    #     time.sleep(0.5)
    #     procCam.trig.sendStopMachine(False)
    #     time.sleep(0.5)
    #     procCam.trig.sendStopMachine(False)
        


@camRouter.on_event("shutdown")
def shutdown():
    time.sleep(2)
    if(procCam.trig.serialHandle.is_open and procCam.cam.camConnected):
        procCam.trig.sendStopMachine(False)
        time.sleep(0.5)
    procCam.stopped.set()
    procCam.disconnect()
    try:
        print('Reset usb')
        # os.popen("sudo modprobe -r usbhid && sleep 5 && sudo modprobe usbhid",'w').write("esec-ai\n")
        # time.sleep(10)
        print('Reset usb OK')
    except:
        print('Reset usb Error')
        pass
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

app.include_router(camRouter)

if __name__ == "__main__":
    try:
        
        #ip,mac = GetIPAddress().getIt()
        uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info", debug = True)
    except KeyboardInterrupt:
        pass

