#https://stackoverflow.com/questions/12081310/python-module-to-change-system-date-and-time
import datetime
import requests
import json
import time
import sys
import os

url = "http://10.151.27.1/Clockservice/api/Datetime"
response = {}
getted = False
while(getted == False):
    try:
        print('Connecting')
        response = requests.get(url,timeout=5)
        if(response.status_code == 200):
            getted = True
            print('Connected')
    except:
        print('re-connected at 5 sec.')
        getted = False
        time.sleep(5)
        pass


    
res = json.loads(response.content)
month = ''
if(res['Month']<10):
    month = '0'+str(res['Month'])
else:
    month = str(res['Month'])
day = ''
if(res['Day']<10):
    day = '0'+str(res['Day'])
else:
    day = str(res['Day'])
    
time = str(res['Hour'])+':'+str(res['Minute'])+':'+str(res['Seccond'])
cmd2 = 'sudo -S date +%Y%m%d%T -s "'+str(res['Year'])+month+day+' '+time+'"'
os.popen(cmd2, 'w').write('esec-ai\n\n')


