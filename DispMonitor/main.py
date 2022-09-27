from proc.mqtt import MQTT
from proc.serialConnect import SerialDispCommunication

mq = MQTT()
serial = SerialDispCommunication()

serial.openSerialPort()

last_ip = ""

def On_Recieve(data):
    serial.sendAllData(data["StopMC"],data["Rate"],data["TriggerCount"],data["IP"])
    #global last_ip
    #ip = data["IP"]
    #print(ip)
    #if(ip != last_ip):
    #    last_ip = ip
    #    serial.sendIP(ip)
    #print(data)
    #serial.send_3_Data(data["StopMC"],data["Rate"],data["TriggerCount"])

mq.callback = On_Recieve

try: 
    a = input()
    serial.closeSerialPort()
    mq.disconnectMQTT()
except KeyboardInterrupt:
    serial.closeSerialPort()
    mq.disconnectMQTT()
