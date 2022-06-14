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

    def topicRateCounter(self,maxProcessTime,intervalScan = 5):
        counterlen = len(self.allTimeProc)
        offset = 100
        if(counterlen == 0):
            self.allTimeProc = []
            return -1,-1,-1
        try:
            
            t1 = int((intervalScan *1000)/(maxProcessTime+(offset*3)))
            t2 = int((intervalScan *1000)/(maxProcessTime))
            print("##CAL##")
            print(t1)
            print(t2)
            print(counterlen)
            print((intervalScan *1000))
            print(maxProcessTime)
            print("#######")
            if(t1>2 and t2 > 3):
                if(counterlen < t1-2 or counterlen > t2):
                    self.allTimeProc = []
                    return -1,-1,-1
        except:
            pass
        print('OK')
        filterData = []
        procTimeTop = maxProcessTime + offset
        procTimeBottom = maxProcessTime - offset
        # print("CAL")
        # print(procTimeBottom)
        # print(procTimeTop)
        for a in self.allTimeProc:
            #print(a)
            if(a > procTimeBottom  and a < procTimeTop):
                #print(a)
                filterData.append(a)
        try:
            minCount = min(filterData)
        except:
            minCount = -1

        try:
            maxCount = max(filterData)
        except:
            maxCount = -1
        try:
            avgCount = self.average(filterData)
        except:
            avgCount = -1
        self.allTimeProc = []
        return avgCount,maxCount,minCount

    def topic(self):
        #subscribe
        sub_grabSignal = '{}/grab'.format(self.machineID)
        pub_statusWorker = '{}/statusWorker'.format(self.machineID)
        return sub_grabSignal,pub_statusWorker
    
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
        topic,_ = self.topic()
        self.mqtt_client.subscribe(topic,qos=0)

    def publish(self,msg):
        if(self.MQTTConnected):
            _,topic = self.topic()
            self.mqtt_client.publish(topic,msg)

    def onMessageMqtt(self,client, userdata,msg):
        topic,_ = self.topic()
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
