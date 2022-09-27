from tendo import singleton
me = singleton.SingleInstance()

import enum
from tracemalloc import stop
from proc.repeatedTimer import RepeatedTimer
import requests
import json
import time
import threading
from proc.mqtt import MQTT
import datetime
import os
from os.path import expanduser
import shutil


class ProcessState(enum.Enum):
    NoProcess = 0,
    Error = 1,
    Finish = 2

class StatusLevel(enum.Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3

class Process:
    def __init__(self):
        self.initialPath()
        self.timer = RepeatedTimer(5,self.callback)
        self.timer.start()
        self.conf = None
        self.getConfig()
        self.getConfig()
        self.pauseFlag = False
        self.secsgemStoped = False
        self.inProcess = False
        self.clearAllData()
        self.mq = MQTT()
        self.mq.setCountRate = True
        self.rejectCounter = 0
        self.countTime = 0
        pass
    
    def calculateRateTrigger(self):
        try:
            avg,_,_ = self.mq.topicRateCounter(self.conf['maxProcessTimePerUnit'],self.conf['inferenceRate'])
            print('Process time avg : {} ms'.format(avg))
            return avg
        except:
            return -1
            pass

    def createDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def initialPath(self):
        pathMain =  '{}/EsecUnitAnormalyDetection/Startup/logs'.format(expanduser("~"))
        pathlog = '{}/logworker'.format(pathMain)
        self.pathImg = '{}/ImgScreenSave'.format(expanduser("~"))
        self.pathSetup = '{}/SetupMode'.format(self.pathImg)
        self.pathProcess = '{}/ProcessMode'.format(self.pathImg)
        self.pathCopyimg = '{}/Reject'.format(self.pathSetup)
        self.createDir(pathMain)
        self.createDir(pathlog)
        self.createDir(self.pathImg)
        self.createDir(self.pathProcess)
        self.createDir(self.pathCopyimg)
        x = datetime.datetime.now()
        return pathMain,pathlog+'/log {}.log'.format(x.strftime('%Y-%m-%d'))

    def statusUpdate(self,msg,statusLevel = StatusLevel.INFO):
        try:
            level = ''
            if(statusLevel == StatusLevel.INFO):
                level = 'INFO'
            elif(statusLevel == StatusLevel.WARNING):
                level = 'WARNING'
            else:
                level = 'ERROR'
            status = '{} {} {}'.format(datetime.datetime.now(),level,msg)
            _,filename = self.initialPath()
            if os.path.exists(filename):
                append_write = 'a' # append if already exists
            else:
                append_write = 'w' # make a new file if not
            with open(filename,append_write) as log:
                log.write(status+'\n')
            print(status)
            self.mq.publish(status)
        except:
            pass

    def updateParam(self):
        try:
            if(self.timer.interval != self.conf['inferenceRate']):
                self.timer.stop()
                time.sleep(2)
                self.timer.interval = self.conf['inferenceRate']
                self.timer.start()
        except Exception as ex:
            return 

    def callback(self):
        
        if(self.inProcess):
            return
        self.getConfig()
        self.updateParam()
        self.secsgemStoped = self.getStopMc()
        if(self.countTime > 12*5):
            self.updateControlMonitor()
        if(self.calculateRateTrigger() == -1):
            self.clearAllData()
            self.statusUpdate('It not proc Mode',StatusLevel.WARNING)
            return
        if(self.pauseFlag):
            self.clearAllData()
            self.statusUpdate('Pause for setup machine.')
            return
        if(self.secsgemStoped):
            stopmc = "SECS/GEM"
            if(self.conf["stopMachine"] == "IO"):
                stopmc = "IO"
            elif(self.conf["stopMachine"] == "BOTH"):
                stopmc = "SECS/GEM and IO"
            else:
                stopmc = "SECS/GEM"
            self.clearAllData()
            self.statusUpdate('Stop machine by {}.'.format(stopmc),StatusLevel.WARNING)
            return
        if(self.conf is None):
            self.statusUpdate('Config Machine error.',StatusLevel.ERROR)
            self.clearAllData()
            return
        if(self.conf['useAI'] == False):
            self.statusUpdate('Do not use AI',StatusLevel.WARNING)
            self.clearAllData()
            return
        
        self.proc()
        
    def proc(self):
        self.inProcess = True
        imgs = self.getImg()
        if(imgs is None):
            self.statusUpdate('Dataset API connection loss',StatusLevel.WARNING)
            self.inProcess = False
            return
        if(len(imgs['imgList']) == 0):
            self.statusUpdate('Waitting For image')
            self.inProcess = False
            return
        res = self.getResult(imgs['imgList'],self.conf['bboxCrop'],self.conf['rejectThreshold'])
        if(res is None):
            self.clearAllData()
            self.statusUpdate('AI Server is busy',StatusLevel.WARNING)
            self.inProcess = False
            return
        # thr = threading.Thread(target=self.deleteImg, args=[imgs['imgList']])
        # thr.start()
        rejCount = self.resultProc(res)
        self.rejectCounter+= rejCount
        if(self.rejectCounter >= self.conf['stopWhenRejectCount']):
            self.rejectCounter = 0
            self.stopMc()
        self.deleteImg(imgs['imgList'])
        # thr.join()
        self.inProcess = False

    def stopMc(self):
        if(self.secsgemStoped):
            return
        self.clearAllData()
        stopmc = "SECS/GEM"
        if(self.conf["stopMachine"] == "IO"):
            stopmc = "IO"
        elif(self.conf["stopMachine"] == "BOTH"):
            stopmc = "SECS/GEM and IO"
        else:
            stopmc = "SECS/GEM"

        self.statusUpdate('Stop machine by {}.'.format(stopmc),StatusLevel.WARNING)

        self.setStopMc()

        time.sleep(1)
        self.clearAllData()
        self.secsgemStoped = True

    def getStopMc(self):
        try:
            url = "http://127.0.0.1:8081/camcontrol/is_stopMachine/"
            response = requests.request("GET", url,timeout=5)
            if(response.status_code != 200):
                self.statusUpdate('Can not connect stop machine server.',StatusLevel.ERROR)
                return False
            return bool(json.loads(response.text))
        except:
            self.statusUpdate('Can not connect stop machine server.',StatusLevel.ERROR)
            return False

    def setStopMc(self,message = None):
        try:
            msg = "Stop%20machine%20by%20AI"
            if(message is not None):
                msg = message.replace(' ', '%20')
            url = "http://127.0.0.1:8081/camcontrol/stopMC/true/msg/{}".format(msg)
            response = requests.request("GET", url,timeout=5)
            if(response.status_code != 200):
                self.statusUpdate('Can not connect stop machine server.',StatusLevel.ERROR)
                return False
            return bool(json.loads(response.text))
        except:
            self.statusUpdate('Can not connect stop machine server.',StatusLevel.ERROR)
            return False


    def clearAllData(self):
        try:
            imgs = self.getImg()
            if(imgs is None):
                return
            if(len(imgs['imgList']) == 0):
                return
            self.deleteImg(imgs['imgList'])
        except:
            return

    def getConfig(self):
        try:
            url = "http://127.0.0.1:8084/config"
            response = requests.request("GET", url,timeout=5)
            try:
                lastmcID = self.conf['machineId']
            except:
                lastmcID = ""
            if(response.status_code == 200):
                self.conf = json.loads(response.text)
            currentmcID = self.conf['machineId']
            if(lastmcID != currentmcID):
                self.updateControlMonitor()
        except:
            pass
    
    def updateControlMonitor(self):
        try:
            url = 'http://127.0.0.1:8081/camcontrol/setDispConfig/{}'.format(self.conf['machineId'])
            response = requests.request("GET", url,timeout=5)
        except:
            pass

    def getImg(self):
        try:
            urlImg = "http://127.0.0.1:8082/filecontrol/images/Process"
            responseImg = requests.request("GET", urlImg,timeout=5)
            if(responseImg.status_code != 200):
                self.statusUpdate(responseImg.text,StatusLevel.ERROR)
                return None
            return json.loads(responseImg.text)
        except:
            self.statusUpdate("Can not connect dataset server",StatusLevel.ERROR)
            return None
    
    def getResult(self,imgs,boxCrop,threshold = None):
        try:
            url = "http://127.0.0.1:8083/ai/infer"
            param = {
                "imgList": imgs,
                "bbox": boxCrop,
                "threshold":threshold
            }
            headers = {'Content-Type': 'application/json'}
            payload = json.dumps(param)
            response = requests.request("POST", url, headers=headers, data=payload,timeout=20)
            if(response.status_code != 200):
                self.statusUpdate(response.text,StatusLevel.ERROR)
                if(response.status_code == 405):
                    self.setStopMc('Stop MC because AI model not yet training.')
                if(response.status_code == 403):
                    self.setStopMc('Stop MC because AI process on training.')
                return None
            return json.loads(response.text)
        except:
            self.statusUpdate("Cannot Connect ai server",StatusLevel.ERROR)
            return None

    def resultProc(self,resAll):
        rejectCount = 0
        for res in resAll:
            if(res['scoreMax'] > self.conf['rejectThreshold']):
                rejectCount += 1
                self.saveImgReject(res)
        self.statusUpdate('ImgAll {} haveReject {}'.format(len(resAll),rejectCount))
        return rejectCount

    def saveImgReject(self,objRes):
        try:
            self.copyRejectImg(objRes['imgfilename'])
            param = [{
                        "imgRaw": objRes['resultImgInput'],
                        "imgHeatMap": objRes['resultImgHeat'],
                        "scoreMin": objRes['scoreMin'],
                        "scoreMax": objRes['scoreMax'],
                        "rejectThreshold": self.conf['rejectThreshold'],
                        "machineNo": self.conf['machineId'],
                        "imgFileName": objRes['imgfilename'].split('.')[0]
                    }]
            url = "http://127.0.0.1:8085/reject_result"
            payload = json.dumps(param)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload,timeout=20)
            print(response.text)
        except:
            pass

    def deleteImg(self,imgs):
        try:
            url = "http://127.0.0.1:8082/filecontrol/images/"
            param = {
                    "mode": "Process",
                    "imgList": imgs
                }
            payload = json.dumps(param)
            headers = {
                'Content-Type': 'application/json'
                }
            response = requests.request("DELETE", url, headers=headers, data=payload)
            if(response.status_code != 200):
                self.statusUpdate(response.text,StatusLevel.ERROR)
                return False
            return True
        except:
            return False




    def copyRejectImg(self,name):
        try:
            src = os.path.join(self.pathProcess,name)
            dst = os.path.join(self.pathCopyimg,"RETRAIN_" + name)
            shutil.copyfile(src, dst)
        except:
            pass
    
if __name__ == '__main__':
    proc = Process()
    #print(Process().getStopMc())
