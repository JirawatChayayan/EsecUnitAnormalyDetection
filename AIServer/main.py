from distutils.log import debug
from statistics import mode
from threading import Thread
from typing import List
from cv2 import threshold

from matplotlib.transforms import Bbox
import json
import glob
from fastapi import FastAPI,Response, status, APIRouter
from sqlalchemy import true
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from AICore.training import Training
import time
training = Training()


class Item(BaseModel):
    imgList:list
    bbox : tuple = None 

class InferModel(BaseModel):
    imgList:list
    bbox : tuple = None
    threshold : int = None



app = FastAPI(
    title="AI Training",
    description="Load and delete file with API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

ai = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={404: {"description": "Not found"}},
)

def listImage():
    list = glob.glob('{}/*.png'.format('/home/esec-ai/ind_knn_ad/datasets/hazelnut_reduced/train/good'))
    return list

inProcess = False
model = False
def trainingProc(imgs,bbox= None):
    global inProcess,training
    inProcess = True
    result = ""
    try:
        training.train(imgs,bbox)
        # del training
        # del Training
        result = "finished"
    except Exception as ex:
        result = "Training_fail {}".format(ex)
    finally:
        inProcess = False
    return result

def inference(imgs,bbox= None,threshold = None):
    global inProcess,training,model
    inProcess = True
    result = None
    try:
        if(training.model == None):
            model = False
            result = None
        else:
            result = training.predict(imgs,bbox,threshold)
            model = True
    except Exception as ex:
        print("Training_fail {}".format(ex))
        result = None
    finally:
        inProcess = False
    return result
    
def inference_disp(imgs,bbox= None):
    global inProcess,training,model
    inProcess = True
    result = None
    try:
        if(training.model == None):
            model = False
            result = None
        else:
            result = training.predict_disp(imgs,bbox)
            model = True
    except Exception as ex:
        print("Training_fail {}".format(ex))
        result = None
    finally:
        inProcess = False
    return result

def getModel():
    global inProcess,training,model
    try:
        if(training.model == None):
            model = False
        else:
            model = True
    except:
        model = False
    return model

def getOntraining():
    global training
    try:
        if(training.onTraining):
            return True
        else:
            return False
    except:
        return False


@ai.post("/train",status_code=200)
def train(item :Item,response:Response):
    global inProcess
    t1 = time.perf_counter()
    if(inProcess):
        response.status_code = 401
        return "inProcess"
    result = trainingProc(item.imgList,item.bbox)
    #print(result)
    if(result == "finished"):
        response.status_code = 200
        t2 = time.perf_counter()
        print(f'Finished in {round(t2-t1, 2)} second(s)')
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result

@ai.post("/infer",status_code=200)
def infer(item :InferModel,response:Response):
    global inProcess
    if(inProcess):
        response.status_code = 401
        return "inProcess"
    if(getOntraining()):
        response.status_code = 403
        return "OnTraining"
    if(getModel() == False):
        response.status_code = 405
        return "noModel"
    result = inference(item.imgList,item.bbox,item.threshold)
    if(result is not None):
        response.status_code = 200
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result

@ai.post("/infer_disp",status_code=200)
def infer(item :Item,response:Response):
    global inProcess
    if(inProcess):
        response.status_code = 401
        return "inProcess"
    if(getOntraining()):
        response.status_code = 403
        return "OnTraining"
    if(getModel() == False):
        response.status_code = 405
        return "noModel"
    result = inference_disp(item.imgList,item.bbox)
    if(result is not None):
        response.status_code = 200
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result

app.include_router(ai)

@app.on_event("startup")
def startup():
    pass

@app.on_event("shutdown")
def shutdown():
    pass
    

if __name__ == '__main__':
    try:
        uvicorn.run(app, host="0.0.0.0", port=8083, log_level="info" ,debug = True)
    except KeyboardInterrupt:
        pass
        


# class ProcessInfer:
#     def __init__(self):
#         self.mqtt = MQTT()
#         self.mqtt.callbackInfer = self.onRecieve
#         self.mqtt.connectMqtt()
#         self.inProcess = False
#         self.infer = Inference()
#         self.infer.callbackResult = self.callbackResult
#         self.infer.callbackStatus = self.callbackStatus
#         pass
    
#     def callbackResult(self,msg):
#         self.mqtt.publish(json.dumps(msg),0)

#     def callbackStatus(self,msg,status : StatusLevel):
#         self.mqtt.statusUpdate(msg,status)

#     def onRecieve(self,msg):
#         if(self.inProcess):
#             self.mqtt.statusUpdate("AI_in process",StatusLevel.WARNING)
#             return
#         try:
#             print(Training().weightFileNamelatest())
#             res = self.infer.predict(listImage(),Training().weightFileNamelatest(),None)
#             if(res is not None):
#                 self.mqtt.publish(json.dumps(res),1)
#         except Exception as ex:
#             self.mqtt.statusUpdate("Inference Process Error {}".format(ex),StatusLevel.ERROR)
#         finally:
#             self.inProcess = False
#         pass


# class ProcessTraining:
#     def __init__(self):
#         self.mqtt = MQTT()
#         self.mqtt.connectMqtt()
#         self.inProcess = False
#         self.mqtt.callbackTrain = self.callback
    
#     def callback(self, msg):
#         if(self.inProcess):
#             self.mqtt.statusUpdate("Training_in process",StatusLevel.WARNING)
#             return
#         self.trainingProc(msg["imgList"],msg["bbox"])

#     def callbackResult(self,msg):
#         self.mqtt.publish(json.dumps(msg),0)

#     def callbackStatus(self,msg,status : StatusLevel):
#         self.mqtt.statusUpdate(msg,status)
#         pass
#     def trainingProc(self,imgs,bbox= None):
#         self.inProcess = True
#         try:
#             #self.training.train(imgs=imgs,boxCrop=bbox)
#             x = Thread(target=train, args=(imgs,bbox,), daemon=True)
#             x.start()
#             x.join()
#         except Exception as ex:
#             self.mqtt.statusUpdate("Training_fail {}".format(ex),StatusLevel.ERROR)
#         finally:
#             self.inProcess = False



# def callbackResult(msg):
#     global inProcess,mqtt
#     mqtt.publish(json.dumps(msg),0)

# def callbackStatus(msg,status : StatusLevel):
#     global inProcess,mqtt
#     mqtt.statusUpdate(msg,status)


# def train(imgs1: list,bbox1:tuple):
#     print(type(imgs1))
#     print(type(bbox1))

# mqtt = MQTT()
# mqtt.connectMqtt()

# def callback(msg):
#     global inProcess,mqtt
#     if(inProcess):
#         mqtt.statusUpdate("Training_in process",StatusLevel.WARNING)
#         return
#     trainingProc(msg["imgList"],msg["bbox"])


#mqtt.callbackTrain = callback
