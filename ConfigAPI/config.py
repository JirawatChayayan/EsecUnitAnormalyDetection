import os
import json
from os.path import expanduser

class AIConfig():
    def __init__(self):
        self.machineId = 'ESEC2008-01P'
        self.rejectThreshold = 120
        self.stopWhenRejectCount = 1
        self.changeModeWhenProcessTrigCount = 20 
        self.maxProcessTimePerUnit = 1
        self.useAI = False
        self.inferenceRate = 5
        self.equipOpn = 'DA'
        self.cimEquipID = 'TDAE096'
        self.stopMachine = 'SECS/GEMS'
        self.bboxCrop = [690,490,915,712]
        self.loadConfig()


    def setnewbbox(self,bbox :list):
        try:
            if(len(bbox) == 4):
                self.bboxCrop = bbox
                self.saveconfig()
                print(self.bboxCrop)
                return True
            else:
                print('ERROR'+' Config format bbox not correct !!! {}'.format(bbox)) 
                return False
        except Exception as ex:
            print('ERROR'+' Config format not correct !!! {}'.format(ex))
            return False

    def setnewConfig(self,newParam):
        try:
            machineId = str(newParam['machineId']).strip()
            rejectThreshold = int(newParam['rejectThreshold'])
            stopWhenRejectCount = int(newParam['stopWhenRejectCount'])
            changeModeWhenProcessTrigCount = int(newParam['changeModeWhenProcessTrigCount'])
            maxProcessTimePerUnit = int(newParam['maxProcessTimePerUnit'])
            useAI = bool(newParam['useAI'])
            inferenceRate = int(newParam['inferenceRate'])
            equipOpn = str(newParam['equipOpn'])
            cimEquipID = str(newParam['cimEquipID'])
            stopMachine = str(newParam['stopMachine'])
            bboxCrop = list(newParam['bboxCrop'])

            self.machineId = machineId
            self.rejectThreshold = rejectThreshold
            self.stopWhenRejectCount = stopWhenRejectCount
            self.changeModeWhenProcessTrigCount = changeModeWhenProcessTrigCount
            self.maxProcessTimePerUnit = maxProcessTimePerUnit
            self.useAI = useAI
            self.inferenceRate = inferenceRate
            self.equipOpn = equipOpn
            self.cimEquipID = cimEquipID
            self.stopMachine = stopMachine
            self.bboxCrop = bboxCrop

            self.saveconfig()
            return True
        except Exception as ex:
            print('ERROR'+' Config format not correct !!! {}'.format(ex))
            return False
    
    def getCurrentConfig(self):
        return  {
                    "machineId" : self.machineId.strip(),
                    "rejectThreshold" : int(self.rejectThreshold),
                    "stopWhenRejectCount" : int(self.stopWhenRejectCount),
                    "changeModeWhenProcessTrigCount" : int(self.changeModeWhenProcessTrigCount),
                    "maxProcessTimePerUnit" :int(self.maxProcessTimePerUnit),
                    "useAI" : self.useAI,
                    "inferenceRate" : self.inferenceRate,
                    "equipOpn" : self.equipOpn,
                    "cimEquipID" : self.cimEquipID,
                    "stopMachine" : self.stopMachine,
                    "bboxCrop" : self.bboxCrop
                }

    def createdir(self):
        config_dir = self.pathConfig()
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def pathConfig(self):
        return '{}/ImgScreenSave/Config'.format(expanduser("~"))
    
    def loadConfig(self):
        try:
            config_dir = os.path.join(self.pathConfig(),'config.json')
            self.createdir()
            param = self.getCurrentConfig()
            if not os.path.exists(config_dir):
                json_data = json.dumps(param, indent=2)
                f = open(config_dir, 'x')
                f.write(json_data)
                f.close()
            with open(config_dir) as file:
                param = json.load(file)
                self.setnewConfig(param)
        except:
            self.saveconfig()
        return param

    def saveconfig(self):
        config_dir = os.path.join(self.pathConfig(),'config.json')
        self.createdir()
        param = self.getCurrentConfig()
        json_data = json.dumps(param, indent=2)
        f = open(config_dir, 'w')
        f.write(json_data)
        f.close()

if __name__ == '__main__':
    config = AIConfig()
    config.loadConfig()
    config.saveconfig()
    print(config.getCurrentConfig())
    #Test Pass