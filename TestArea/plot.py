# Import Libraries

from turtle import color
import matplotlib.pyplot as plt
import datetime
import numpy as np
import pandas as pd
import requests
import json
import base64
import io


def getData():
    url = "http://0.0.0.0:8085/all_result/lotAnomalyInfo"
    payload = json.dumps({
        "lotNo": "TESTT5555.5",
        "lotNoCount": 1
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)


def plotData():
    data = getData()
    fig = plt.figure()

    rangeData = list(range(1,len(data['datetime'])+1))


    print(len(rangeData))
    print(len(data['datetime']))
    df_ams = pd.DataFrame({
        "date" : data['datetime'],
        "ams" : data['scoreMax'],
        "defect_percent" : data['defectPercent'],
        "setup_value" : data['setupValue'],
        "proc_mode":data['procMode'],
        "range" : rangeData
    })

    plt.plot(df_ams.range, df_ams.defect_percent, label='Anormaly_MaxScore',color = 'lightskyblue', linewidth=1)
    plt.plot(df_ams.range, df_ams.setup_value, label='Setup_Value',color = 'crimson', linewidth=1)
    plt.title('Anormaly Lot XXX Summary')
    plt.xlabel('Date')
    plt.ylabel('Scale')
    plt.tick_params(axis='x',labelsize=10,rotation=90)
    plt.legend()
    plt.tight_layout()
    plt.show() 

def plotGraph(unitRange,data1,data2,caption1,caption2,graph_title,x_label,y_label):
    df = pd.DataFrame({
        "data1" : data1,
        "data2" : data2,
        "range" : unitRange
    })
    fig = plt.figure(figsize=(10,5))
    plt.plot(df.range, df.data1, label=caption1,color = 'royalblue', linewidth=2)
    plt.plot(df.range, df.data2, label=caption2,color = 'crimson', linewidth=2)

    plt.title(graph_title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.tight_layout()
    bytesImgInput = io.BytesIO()
    fig.savefig(bytesImgInput, format='jpg', bbox_inches='tight', pad_inches=0, transparent=False)
    bytesImgInput.seek(0)
    base64ImgInput = base64.b64encode(bytesImgInput.read())
    strBase64Img = str(base64ImgInput)[2:-1]
    #plt.show()
    plt.cla()
    plt.clf()
    plt.close()
    plt.close('all')
    del fig

    return  "data:image/jpg;base64,{}".format(strBase64Img)

def plot():
    datas = getData()
    if(datas is None):
        raise Exception('Get data error !!!')
    proc1Data = datas['procMode1']
    proc2Data = datas['procMode2']
    proc3Data = datas['procMode3']


    res = {
        'procMode1' : None,
        'procMode2' : None,
        'procMode3' : None
    }

    if(proc1Data is not None):
        #plotdata ams
        # allUnit = proc1Data['unitCount'][-1]
        rejectUnit = 0
        i = 0
        allUnit = 0
        for a in proc1Data['scoreMax']:
            allUnit +=1
            if(a > proc1Data['setupValue'][i]):
                rejectUnit += 1
            i+=1
        res['procMode1'] = plotGraph(proc1Data['unitCount'],
                  proc1Data['scoreMax'],
                  proc1Data['setupValue'],
                  'unit_anomaly_score',
                  'reject_threshold_value',
                  f'Anormaly max score Lot XXX summary {allUnit} unit reject {rejectUnit} unit.',                  
                  "Number of unit run",
                  "Anormaly score")

    if(proc2Data is not None):
        #plotdata ams
        allUnit = 0#proc2Data['unitCount'][-1]
        rejectUnit = 0
        i = 0
        for a in proc2Data['defectPercent']:
            allUnit += 1
            if(a > proc2Data['setupValue'][i]):
                rejectUnit += 1
            i+=1
        res['procMode2'] = plotGraph(proc2Data['unitCount'],
                proc2Data['defectPercent'],
                proc2Data['setupValue'],
                'unit_anomaly_percent',
                'reject_anomaly_percent',
                f'Unit anomaly Lot XXX summary {allUnit} unit reject {rejectUnit} unit.',                  
                "Number of unit run",
                "Anormaly percent")

    if(proc3Data is not None):
        #plotdata ams
        allUnit = 0#proc3Data['unitCount'][-1]
        rejectUnit = 0
        i = 0
        for a in proc3Data['defectPercent']:
            allUnit +=1
            if(a > proc3Data['setupValue'][i]):
                rejectUnit += 1
            i+=1
        res['procMode3'] = plotGraph(proc3Data['unitCount'],
                proc3Data['defectPercent'],
                proc3Data['setupValue'],
                'unit_anomaly_area_percent',
                'reject_anomaly_area_percent',
                f'Unit anomaly Lot XXX summary {allUnit} unit reject {rejectUnit} unit.',                  
                "Number of unit run",
                "Anormaly area percent")

    return res



a = plot()

#print(json.dumps(a,indent=4))

# # Create figure

# fig = plt.figure(figsize=(26, 16))

# # Define Data

# df1 = pd.DataFrame({'date': np.array([datetime.datetime(2021, 
#                     12, i+1) for i in range(20)]),
#                    'blogs_read': [4, 6, 5, 8, 15, 13, 18, 6, 5, 
#                   3, 15, 14, 19, 21, 15, 19, 25, 24, 16, 26]})

# df2 = pd.DataFrame({'date': np.array([datetime.datetime(2021, 
#                      12, i+1)
#  for i in range(20)]),
#                    'blogs_unread': [1, 1, 2, 3, 3, 3, 4, 3, 2,     
#                     3, 4, 7, 5, 3, 2, 4, 3, 6, 1, 2]})

# # Plot time series

# plt.plot(df1.date, df1.blogs_read, label='blogs_read', 
#          linewidth=3)
# plt.plot(df2.date, df2.blogs_unread, color='red', 
#          label='blogs_unread', linewidth=3)

# # Add title and labels

# plt.title('Blogs by Date')
# plt.xlabel('Date')
# plt.ylabel('Blogs')

# # Add legend

# plt.legend()

# # Auto space

# plt.tight_layout()

# # Display plot

# plt.show() 