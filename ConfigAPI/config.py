import os
import json

class AIConfig():
    def __init__(self):
        self.machineId = 'ESEC2008-01P'
        self.rejectThreshold = 120
        self.stopWhenRejectCount = 1
        self.changeModeWhenProcessTrigCount = 20 
        self.useAI = False
        self.inferenceRate = 5
        self.bboxCrop = [690,490,915,712]
        self.loadConfig()



    def setnewConfig(self,newParam):
        try:
            machineId = str(newParam['machineId']).strip()
            rejectThreshold = int(newParam['rejectThreshold'])
            stopWhenRejectCount = int(newParam['stopWhenRejectCount'])
            changeModeWhenProcessTrigCount = int(newParam['changeModeWhenProcessTrigCount'])
            useAI = bool(newParam['useAI'])
            inferenceRate = int(newParam['inferenceRate'])
            bboxCrop = list(newParam['bboxCrop'])

            self.machineId = machineId
            self.rejectThreshold = rejectThreshold
            self.stopWhenRejectCount = stopWhenRejectCount
            self.changeModeWhenProcessTrigCount = changeModeWhenProcessTrigCount
            self.useAI = useAI
            self.inferenceRate = inferenceRate
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
                    "useAI" : self.useAI,
                    "inferenceRate" : self.inferenceRate,
                    "bboxCrop" : self.bboxCrop
                }

    def createdir(self):
        config_dir = self.pathConfig()
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def pathConfig(self):
        return '/home/esec-ai/ImgScreenSave/Config'
    
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