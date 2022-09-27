import os
import time
from proc.mqtt import MQTT
from datetime import datetime


print('Service start At {}\n'.format(datetime.now()))

previos = int(time.time())

def mqCallBack(res):
    global previos
    previos = int(time.time())
    #print('{} {}'.format(datetime.now(),res))

mq = MQTT()
mq.callback = mqCallBack

while(True):
    t = int(time.time()) - previos
    time.sleep(1)

    if(t > 50):
        print('Reboot At {}\n'.format(datetime.now()))
        mq.disconnectMQTT()
        time.sleep(2)
        break

        
os.popen("sudo -S %s"%('reboot'), 'w').write('j\n')



