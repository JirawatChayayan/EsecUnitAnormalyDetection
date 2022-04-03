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
            if(self.callback is not None):
                mode = json.loads(data)['modeRun']
                if(mode == 1):
                    self.callback(1)
                else:
                    self.callback(2)
