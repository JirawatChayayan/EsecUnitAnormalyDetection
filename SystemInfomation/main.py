import psutil
import time
import os
import json
from proc.mqtt import MQTT

mq = MQTT()
hdd = psutil.disk_usage('/')
f_cpu = psutil.cpu_freq(percpu=False)
ram = psutil.virtual_memory()

try:
    core_Temp = psutil.sensors_temperatures()['coretemp'][0]
except:
    pass
homepath = os.path.expanduser("~")
path = "{}/ImgScreenSave/SetupMode/TempolaryTest".format(homepath)
def get_folder():
    global path
    dir = os.listdir(path)
    return dir

def listFile():
    global path
    filename = []
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            filename.append(name)
    return filename

# print(get_folder())
# listFile()
while(True):
    try:
        hdd = psutil.disk_usage('/')
        f_cpu = psutil.cpu_freq(percpu=False)
        ram = psutil.virtual_memory()
        
        # print(float(core_Temp.current))
        objData = dict()
        try:
            core_Temp = psutil.sensors_temperatures()['coretemp'][0]
            objData["CPU_Temp"] = float(core_Temp.current)
        except:
            pass
        
        try:
            objData["CPU_Percent"] = psutil.cpu_percent(4)
            objData["CPU_Max_Frequency"] = int(f_cpu.max)
            objData["CPU_Current_Frequency"] = int(f_cpu.current)
        except:
            pass
        objData["Ram_Total"] = float("{:.2f}".format(ram.total/ (2**30)))
        objData["Ram_Used"] = float("{:.2f}".format(ram.used / (2**30)))
        objData["Ram_Free"] = float("{:.2f}".format(ram.free / (2**30)))
        
        objData["HDD_Total"] = float("{:.2f}".format(hdd.total/ (2**30)))
        objData["HDD_Used"] = float("{:.2f}".format(hdd.used / (2**30)))
        objData["HDD_Free"] = float("{:.2f}".format(hdd.free / (2**30)))

        objData["LogFolder"] = len(get_folder())
        objData["LogImage"] = len(listFile())

        data = json.dumps(objData,indent=4)
        print(data)
        mq.publish(data)
    except Exception as e:
        print(e)
        pass
    time.sleep(0.2)

#print(psutil.sensors_temperatures())