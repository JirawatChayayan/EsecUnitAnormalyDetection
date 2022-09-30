import csv
import shutil
import glob
import natsort
import os
from datetime import datetime
# print(glob.glob("/home/adam/*"))

# shutil.copyfile(src, dst)
# shutil.copy(src, dst)  


pathMain = "/home/j/ImgScreenSave/SetupMode/Train"

pathDest = "/home/j/AnormalyResultAll/Image/ImageTrain"



# fileInMain = glob.glob(pathMain,"*")
# print(fileInMain)


#imgsPathTrain = natsort.natsorted([os.path.abspath(os.path.join(pathMain, p)) for p in os.listdir(pathMain)])

pathCSVTrain = "/home/j/AnormalyResultAll/CSV/CSV-Train"

def writeCSVTrain(lotNo,fileList):
    global pathCSVTrain
    csvPath = os.path.join(pathCSVTrain,f"{lotNo.strip()}.csv")
    fHandle = None 
    writer = None
    if(os.path.exists(csvPath) == False):
        fHandle = open(csvPath, 'w',newline='')
        writer = csv.writer(fHandle)
        row = ["FileNameList"]
        writer.writerow(row)
    else:
        fHandle = open(csvPath, 'a')
        writer = csv.writer(fHandle)
        now = datetime.now()
        date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        row = [""]
        writer.writerow(row)
        row = [f"Append On {date_time_str}"]
        writer.writerow(row)

    for a in fileList:
        row = [a]
        writer.writerow(row)

    if(fHandle is not None):
        fHandle.close()

def copyFileIfNotExit(src,dest):
    imgsPath = natsort.natsorted([os.path.abspath(os.path.join(src, p)) for p in os.listdir(src)])
    
    imgsfile = []
    
    for imgFile in imgsPath:
        fName = os.path.basename(imgFile)
        destFilePath = os.path.join(dest,fName)

        if(os.path.exists(destFilePath) == False):
            try:
                shutil.copyfile(imgFile, destFilePath)
                print(f"File Copies {fName}")
                imgsfile.append(fName)
            except:
                print(f"File notfound {fName}")
        else:
            print(f"Have {fName} file in destination path.")
            imgsfile.append(fName)
   
    writeCSVTrain("data-lot",imgsfile)

copyFileIfNotExit(pathMain,pathDest)

