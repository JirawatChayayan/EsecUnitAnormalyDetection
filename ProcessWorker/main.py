import enum
from tracemalloc import stop
from proc.repeatedTimer import RepeatedTimer
import requests
import json
import time
import threading
from proc.mqtt import MQTT

class ProcessState(enum.Enum):
    NoProcess = 0,
    Error = 1,
    Finish = 2


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
        pass
    
    def callbackMQ(self,mode):
        if(mode == 1):
            print('mode 1')
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
            print('mode 2')
            self.counterSetup +=1
            if(self.counterSetup >5):
                self.pauseFlag = True


    
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
        if(self.secsgemStoped):
            print('Stop machine by secs/gems.')
            return
        if(self.conf is None):
            return
        if(self.conf['useAI'] == False):
            return
        if(self.pauseFlag):
            return
        self.proc()
        
    def proc(self):
        self.inProcess = True
        imgs = self.getImg()
        if(imgs is None):
            print('Dataset API connection loss')
            self.inProcess = False
            return
        if(len(imgs['imgList']) == 0):
            print('Waitting For image')
            self.inProcess = False
            return
        res = self.getResult(imgs['imgList'],self.conf['bboxCrop'])
        if(res is None):
            self.inProcess = False
            return
        thr = threading.Thread(target=self.deleteImg, args=[imgs['imgList']])
        thr.start()
        rejCount = self.resultProc(res)
        print('Reject Count : {}'.format(rejCount))
        if(rejCount >= self.conf['stopWhenRejectCount']):
            self.stopMc()
        thr.join()
        self.inProcess = False

    def stopMc(self):
        if(self.secsgemStoped):
            return
        self.clearAllData()
        print('McStoped')
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
        urlImg = "http://0.0.0.0:8082/filecontrol/images/Process"
        responseImg = requests.request("GET", urlImg)
        if(responseImg.status_code != 200):
            print('Error {}'.format(responseImg.text))
            return None
        return json.loads(responseImg.text)
    
    def getResult(self,imgs,boxCrop):
        url = "http://0.0.0.0:8083/ai/infer"
        param = {
            "imgList": imgs,
            "bbox": boxCrop
        }
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps(param)
        response = requests.request("POST", url, headers=headers, data=payload)
        if(response.status_code != 200):
            print('Error {}'.format(response.text))
            return None
        return json.loads(response.text)

    def resultProc(self,resAll):
        rejectCount = 0
        for res in resAll:
            if(res['scoreMax'] >= self.conf['rejectThreshold']):
                rejectCount += 1
        return rejectCount

    def deleteImg(self,imgs):
        url = "http://0.0.0.0:8082/filecontrol/images/"
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
            print('Error {}'.format(response.text))
            return False
        return True

if __name__ == '__main__':
    try:
        proc = Process()
    except KeyboardInterrupt:
        pass