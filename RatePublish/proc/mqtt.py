from platform import mac_ver
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime


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
            "TriggerCount":0,
            "ip":"127.0.0.1"
        }

        now = datetime.now()
        self.dataFromMicro["LastData"] = "{}-{}-{} {}:{}:{}".format(now.day,now.month,now.year,now.hour,now.minute,now.second)



    def topic(self):
        #subscribe
        sub_Rate = '{}/Rate'.format(self.machineID)
        return sub_Rate
    
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
        rate_topic = self.topic()
        self.mqtt_client.subscribe(rate_topic,qos=0)

    def onMessageMqtt(self,client, userdata,msg):
        rate_topic = self.topic()
        data = str(msg.payload.decode("utf-8"))
        if(msg.topic == rate_topic):
            try:
                self.dataFromMicro = json.loads(data)
                now = datetime.now()
                self.dataFromMicro["LastData"] = "{}-{}-{} {}:{}:{}".format(now.day,now.month,now.year,now.hour,now.minute,now.second)

                #print(self.dataFromMicro)
                if(self.callback is not None):
                    self.callback(self.dataFromMicro)
            except:
                pass
