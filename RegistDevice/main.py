import requests
import json
import os
from getip import GetIPAddress


def getip():
    a = GetIPAddress()
    return a.getIt()

def getConfig():
    try:
        url = "http://127.0.0.1:8084/config"
        response = requests.request("GET", url,timeout=5)
        if(response.status_code == 200):
            return json.loads(response.text)['machineId']
        return None
    except:
        return None

def readHostname():
    myhost = os.uname()[1]
    #print(myhost)
    return myhost

def postData():
    url = "http://10.151.27.1:8086/info"

    ip,mac = getip()
    mc_id = getConfig()
    if(ip == '127.0.0.1' or mac == None or mc_id == None):
        return

    payload = json.dumps({
    "machine_id": mc_id.strip(),
    "machine_ip": ip,
    "mac_address": mac,
    "device_id": readHostname()
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload,timeout=5)

    print(response.text)

if __name__ == '__main__':
    postData()