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
        self.machineID = 'AI'
        self.connectMqtt()

    def publish(self,msg):
        if(self.MQTTConnected):
            topic = self.topic()
            self.mqtt_client.publish(topic,msg)

    def topic(self):
        #subscribe
        pub = '{}/SystemInfo'.format(self.machineID)
        return pub
    
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

