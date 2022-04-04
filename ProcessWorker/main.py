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
        self.timer = RepeatedTimer(5,self.callback)
        self.timer.start()
        self.conf = None
        self.pauseFlag = False
        self.secsgemStoped = False
        self.inProcess = False
        self.clearAllData()
        self.mq = MQTT()
        self.mq.callback = self.callbackMQ
        self.counterProcess = 0
        self.counterSetup = 0
        self.initialPath()
        pass
    
    def callbackMQ(self,mode):
        if(mode == 1):
            if(self.pauseFlag == True):
                if(self.counterSetup > 0):
                    self.counterSetup = 0
                self.counterSetup -=1
            if(self.counterSetup <= -5):
                self.pauseFlag = False
                self.counterSetup = 0
            if(self.secsgemStoped == False):
                return
            self.counterProcess +=1
            if(self.counterProcess >= self.conf['changeModeWhenProcessTrigCount']):
                self.counterProcess = 0
                self.clearAllData()
                self.secsgemStoped = False

            pass
        else:
            if(self.counterSetup < 0):
                self.counterSetup = 0
            self.counterSetup +=1
            if(self.counterSetup >5):
                self.pauseFlag = True
                self.counterSetup = 0
                if(self.secsgemStoped):
                    self.counterSetup = 0
                    self.clearAllData()
                    self.secsgemStoped = False
    
    def createDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def initialPath(self):
        pathMain =  '{}/ImgScreenSave'.format(expanduser("~"))
        pathlog = '{}/logworker'.format(pathMain)
        self.createDir(pathMain)
        self.createDir(pathlog)
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
        if(self.pauseFlag):
            self.statusUpdate('Pause for setup machine.')
            return
        if(self.secsgemStoped):
            self.statusUpdate('Stop machine by secs/gems.',StatusLevel.WARNING)
            return
        if(self.conf is None):
            self.statusUpdate('Config Machine error.',StatusLevel.ERROR)
            return
        if(self.conf['useAI'] == False):
            self.statusUpdate('Do not use AI',StatusLevel.WARNING)
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
        res = self.getResult(imgs['imgList'],self.conf['bboxCrop'])
        if(res is None):
            self.statusUpdate('AI Server is busy',StatusLevel.WARNING)
            self.inProcess = False
            return
        thr = threading.Thread(target=self.deleteImg, args=[imgs['imgList']])
        thr.start()
        rejCount = self.resultProc(res)
        if(rejCount >= self.conf['stopWhenRejectCount']):
            self.stopMc()
        thr.join()
        self.inProcess = False

    def stopMc(self):
        if(self.secsgemStoped):
            return
        self.clearAllData()
        self.statusUpdate('Stop machine by secs/gems.',StatusLevel.WARNING)
        time.sleep(10)
        self.clearAllData()
        self.secsgemStoped = True

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
        url = "http://127.0.0.1:8084/config"
        response = requests.request("GET", url)
        if(response.status_code == 200):
            self.conf = json.loads(response.text)
    
    def getImg(self):
        urlImg = "http://127.0.0.1:8082/filecontrol/images/Process"
        responseImg = requests.request("GET", urlImg)
        if(responseImg.status_code != 200):
            self.statusUpdate(responseImg.text,StatusLevel.ERROR)
            return None
        return json.loads(responseImg.text)
    
    def getResult(self,imgs,boxCrop):
        url = "http://127.0.0.1:8083/ai/infer"
        param = {
            "imgList": imgs,
            "bbox": boxCrop
        }
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps(param)
        response = requests.request("POST", url, headers=headers, data=payload)
        if(response.status_code != 200):
            self.statusUpdate(response.text,StatusLevel.ERROR)
            return None
        return json.loads(response.text)

    def resultProc(self,resAll):
        rejectCount = 0
        for res in resAll:
            if(res['scoreMax'] >= self.conf['rejectThreshold']):
                rejectCount += 1
        self.statusUpdate('ImgAll {} haveReject {}'.format(len(resAll),rejectCount))
        return rejectCount

    def deleteImg(self,imgs):
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

if __name__ == '__main__':
    proc = Process()
