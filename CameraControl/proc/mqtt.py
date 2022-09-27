import paho.mqtt.client as mqtt
import json
from proc.serialConnect import ModeRun
import time


class MQTT:
    def __init__(self):
        self.MQTTserver = '127.0.0.1'
        self.MQTTConnected = False
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.onConnectedMqtt
        self.machineID = 'AI'
        self.previousMode = []

    def topic(self):
        #publish
        pub_modeChange = '{}/mode'.format(self.machineID)
        pub_grabSignal = '{}/grab'.format(self.machineID)
        pub_RateTrigger = '{}/Rate'.format(self.machineID)
        return [pub_modeChange,pub_grabSignal,pub_RateTrigger]
    
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

    def publish(self,msg,i):
        print(msg)
        if(self.MQTTConnected):
            topic = self.topic()
            self.mqtt_client.publish(topic[i],msg)
    
    def sendGrabSignal(self,modeRun,filename):
        try:
            run = 1
            if(modeRun == ModeRun.Process):
                run = 1
            else:
                run = 2
            param = {
                        "modeRun":run,
                        "fileName":filename,
            }
            self.publish(json.dumps(param),1)
        except:
            pass
    def sendModeChange(self,modeRun):
        try:
            if(modeRun == self.previousMode):
                return
            run = 1
            if(modeRun == ModeRun.Process):
                run = 2
            else:
                run = 1
            param = {
                        "modeRun": run
            }
            data = json.dumps(param)
            self.publish(data,0)
            self.previousMode = modeRun
        except Exception as e:
            print(e)
            pass
    def sendRate(self,rate,mcState,trigCount,ip):
        param = {
            "StopMC":mcState,
            "Rate":rate,
            "TriggerCount":trigCount,
            "IP":ip
        }
        data = json.dumps(param)
        self.publish(data,2)
