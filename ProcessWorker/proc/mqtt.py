from platform import mac_ver
import paho.mqtt.client as mqtt
import json
import time


class MQTT:
    def __init__(self):
        self.MQTTserver = '127.0.0.1'
        self.MQTTConnected = False
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.onConnectedMqtt
        self.mqtt_client.on_message = self.onMessageMqtt
        self.machineID = 'AI'
        self.callback = None
        self.connectMqtt()


        self.setCountRate = False
        self.StartedCount = False
        self.allTimeProc = []
        self.lastTime = 0

        self.dataFromMicro = {
            "StopMC":True,
            "Rate":0,
            "TriggerCount":0
        }

    def toggleCounter(self):
        if(self.setCountRate == False):
            return
        if(self.StartedCount == False):
            self.lastTime = time.perf_counter()
            self.StartedCount = True
        else:
            t = int((time.perf_counter()-self.lastTime)*1000)
            self.allTimeProc.append(t)
            self.StartedCount = False
            self.lastTime = 0
        pass

    def average(self,lst):
        return sum(lst) / len(lst)

    def topicRateCounter(self,maxProcessTime,interval = 5):
        intervalScan = 5
        rate = self.dataFromMicro['Rate'],self.dataFromMicro['Rate'],self.dataFromMicro['Rate']
        
        bestCase =  (int)(intervalScan*1000/maxProcessTime)
        print('Best Case := {}'.format(bestCase))
        
        if(rate[0] <= 750):
            bestCaseOK = (self.dataFromMicro['TriggerCount'] > bestCase-2 and self.dataFromMicro['TriggerCount'] < bestCase+2)
            RateOK = (maxProcessTime >= rate[0]-100 and maxProcessTime <= rate[0]+100)
            if(RateOK and bestCaseOK):
                return rate
        else:
            bestCaseOK = (self.dataFromMicro['TriggerCount'] > bestCase-2 and self.dataFromMicro['TriggerCount'] < bestCase+4)
            RateOK = (maxProcessTime >= rate[0]-250 and maxProcessTime <= rate[0]+400)
            if(RateOK and bestCaseOK):
                return rate
        return -1,-1,-1
        

    def topic(self):
        #subscribe
        sub_grabSignal = '{}/grab'.format(self.machineID)
        sub_Rate = '{}/Rate'.format(self.machineID)
        pub_statusWorker = '{}/statusWorker'.format(self.machineID)
        return sub_grabSignal,pub_statusWorker,sub_Rate
    
    def connectMqtt(self):
        if(self.MQTTConnected):
            return
        try:
            print('Connecting')
            port = 1883
            self.mqtt_client.connect(self.MQTTserver, port)
            self.mqtt_client.loop_start()
        except:
            self.MQTTConnected = False
            pass
    
    def disconnectMQTT(self):
        try:
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()
        except:
            pass
    
    def onConnectedMqtt(self,client, userdata, flags, rc):
        time.sleep(2)
        print('Connected.')
        self.MQTTConnected = True
        topic,_,rate_topic = self.topic()
        self.mqtt_client.subscribe(topic,qos=0)
        self.mqtt_client.subscribe(rate_topic,qos=0)

    def publish(self,msg):
        if(self.MQTTConnected):
            _,topic,_ = self.topic()
            self.mqtt_client.publish(topic,msg)

    def onMessageMqtt(self,client, userdata,msg):
        topic,_,rate_topic = self.topic()
        data = str(msg.payload.decode("utf-8"))
        if(msg.topic == topic):
            try:
                mode = json.loads(data)['modeRun']
                if(mode == 1):
                    self.toggleCounter()
                if(self.callback is not None):
                    if(mode == 1):
                        self.callback(1)
                    else:
                        self.callback(2)
            except:
                pass
        if(msg.topic == rate_topic):
            try:
                self.dataFromMicro = json.loads(data)
                print(self.dataFromMicro)
            except:
                pass
