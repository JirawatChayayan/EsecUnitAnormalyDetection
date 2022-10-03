from ast import Param
import os
import json
from os.path import expanduser
from model import ConfigModel, bbox,processParameter,controlParameter,controlParameterInt

class AIConfig():
    def __init__(self):
        self.machineId = 'ESEC2008-01P'
        self.stopWhenRejectCount = 1
        self.changeModeWhenProcessTrigCount = 20 
        self.maxProcessTimePerUnit = 1170
        self.useAI = False
        self.inferenceRate = 5
        self.modeInspect = 2
        self.useStopMachine = False
        self.bboxCrop = {
            "R1" : 194,
            "C1" : 279,
            "R2" : 194,
            "C2" : 279,
        }

        self.processParameter = {
            "RejectByAMS" : {
                "Val" : 150,
                "Min" : 100,
                "Max" : 180
            },
            "RejectByPixelPercent" : {
                "Val" : 3.00,
                "Min" : 1.00,
                "Max" : 5.00
            },
            "RejectByAreaPercent" : {
                "Val" : 3.00,
                "Min" : 1.00,
                "Max" : 5.00
            },
        }

        self.modeInspectDetail = {
            1 : "AnormalyMaxScore",
            2 : "AnormalyRejectPosition",
            3 : "AnormalyRejactArea"
        }

        self.loadConfig()


    def setnewbbox(self,bbox:bbox, save = True):
        try:
            if(bbox is not None):
                self.bboxCrop['R1'] = bbox.R1
                self.bboxCrop['C1'] = bbox.C1
                self.bboxCrop['R2'] = bbox.R2
                self.bboxCrop['C2'] = bbox.C2
                if(save):
                    self.saveconfig()
                print(self.bboxCrop)
                return True
            else:
                print('ERROR'+' Config format bbox not correct !!! {}'.format(bbox)) 
                return False
        except Exception as ex:
            print('ERROR'+' Config format not correct !!! {}'.format(ex))
            return False
    
    def setModeRun(self,modeInspect: int, save = True):
        try:
            if(modeInspect<1 or modeInspect>4):
                return
            self.modeInspect = modeInspect
            if(save):
                self.saveconfig()
        except Exception as ex:
            print('ERROR !!!'+' {}'.format(ex))
            return False


    #ModeInspection
    def getModeInspect(self):
        return self.modeInspectDetail

    #Pixel Percent
    def setRejectByPixelPercent(self,pixelPercent:float = 1.00,save = True):
        try:
            if(pixelPercent <0):
                return False
            
            var = self.processParameter["RejectByPixelPercent"]
            if(pixelPercent < var["Min"] or pixelPercent > var["Max"]):
                return False
            self.processParameter["RejectByPixelPercent"]["Val"] = pixelPercent
            if(save):
                self.saveconfig()
            return True
        except Exception as ex:
            print('ERROR !!!'+' {}'.format(ex))
            return False

    def setRejectByPixelPercentParam(self,param:controlParameter,save = True):
        try:
            if(param is None):
                return False
            if(param.Min > param.Val or param.Max < param.Val):
                return False
            self.processParameter["RejectByPixelPercent"]["Val"] = param.Val
            self.processParameter["RejectByPixelPercent"]["Max"] = param.Max
            self.processParameter["RejectByPixelPercent"]["Min"] = param.Min
            if(save):
                self.saveconfig()
            return True
        except Exception as ex:
            print('ERROR !!!'+' {}'.format(ex))
            return False

    def getRejectByPixelPercentParam(self):
        return self.processParameter["RejectByPixelPercent"]

    #Area Percent
    def setRejectByAreaPercent(self,areaPercent:float =1.00,save = True):
        try:
            if(areaPercent <0):
                return False

            var = self.processParameter["RejectByAreaPercent"]
            if(areaPercent < var["Min"] or areaPercent > var["Max"]):
                return False
            self.processParameter["RejectByAreaPercent"]["Val"] = areaPercent
            if(save):
                self.saveconfig()
            return True
        except Exception as ex:
            print('ERROR !!!'+' {}'.format(ex))
            return False
    
    def setRejectByAreaPercentParam(self,param:controlParameter,save = True):
        try:
            if(param is None):
                return False
            if(param.Min > param.Val or param.Max < param.Val):
                return False
            self.processParameter["RejectByAreaPercent"]["Val"] = param.Val
            self.processParameter["RejectByAreaPercent"]["Min"] = param.Min
            self.processParameter["RejectByAreaPercent"]["Max"] = param.Max
            if(save):
                self.saveconfig()
            return True
        except Exception as ex:
            print('ERROR !!!'+' {}'.format(ex))
            return False

    def getRejectByAreaPercentParam(self):
        return self.processParameter["RejectByAreaPercent"]

    #AMS Param
    def setRejectByAMS(self,ams = 150,save = True):
        try:
            if(ams <0):
                return False
            var = self.processParameter["RejectByAMS"]
            if(ams < var["Min"] or ams > var["Max"]):
                return False
            self.processParameter["RejectByAMS"]["Val"] = ams
            if(save):
                self.saveconfig()
            return True
        except Exception as ex:
            print('ERROR !!!'+' {}'.format(ex))
            return False

    def setRejectByAMSParam(self,amsParam:controlParameterInt,save = True):
        try:
            if(amsParam is None):
                return False
            if(amsParam.Min > amsParam.Val or amsParam.Max < amsParam.Val):
                return False
            self.processParameter["RejectByAMS"]["Val"] = amsParam.Val
            self.processParameter["RejectByAMS"]["Min"] = amsParam.Min
            self.processParameter["RejectByAMS"]["Max"] = amsParam.Max
            if(save):
                self.saveconfig()
            return True
        except Exception as ex:
            print('ERROR !!!'+' {}'.format(ex))
            return False

    def getRejectByAMSParam(self):
        return self.processParameter["RejectByAMS"]




    def setnewConfig2(self,newParam:ConfigModel):
        try:
            machineId = str(newParam.machineId).strip()
            stopWhenRejectCount = int(newParam.stopWhenRejectCount)
            changeModeWhenProcessTrigCount = int(newParam.changeModeWhenProcessTrigCount)
            maxProcessTimePerUnit = int(newParam.maxProcessTimePerUnit)
            useAI = bool(newParam.useAI)
            inferenceRate = int(newParam.inferenceRate)
            modeInspec = int(newParam.modeInspect)
            useStopMachine = bool(newParam.useStopMachine)

            self.machineId = machineId
            self.stopWhenRejectCount = stopWhenRejectCount
            self.changeModeWhenProcessTrigCount = changeModeWhenProcessTrigCount
            self.maxProcessTimePerUnit = maxProcessTimePerUnit
            self.useAI = useAI
            self.inferenceRate = inferenceRate
            self.modeInspect = modeInspec
            self.useStopMachine = useStopMachine
            self.saveconfig()
            return True
        except Exception as ex:
            print('ERROR'+' Config format not correct !!! {}'.format(ex))
            return False

    def setnewConfig(self,newParam):
        try:
            machineId = str(newParam['machineId']).strip()
            stopWhenRejectCount = int(newParam['stopWhenRejectCount'])
            changeModeWhenProcessTrigCount = int(newParam['changeModeWhenProcessTrigCount'])
            maxProcessTimePerUnit = int(newParam['maxProcessTimePerUnit'])
            useAI = bool(newParam['useAI'])
            inferenceRate = int(newParam['inferenceRate'])
            modeInspec = int(newParam['modeInspect'])
            useStopMachine = bool(newParam['useStopMachine'])

            R1 = int(newParam['bboxCrop']['R1'])
            C1 = int(newParam['bboxCrop']['C1'])
            R2 = int(newParam['bboxCrop']['R2'])
            C2 = int(newParam['bboxCrop']['C2'])

            procParam = newParam['processParameter']
            rejPixPercent = procParam['RejectByPixelPercent']
            rejAreaPercent = procParam['RejectByAreaPercent']
            rejByAMS = procParam['RejectByAMS']

            rejPixVal = float(rejPixPercent["Val"])
            rejPixMin = float(rejPixPercent["Min"])
            rejPixMax = float(rejPixPercent["Max"])

            rejAreaVal = float(rejAreaPercent["Val"])
            rejAreaMin = float(rejAreaPercent["Min"])
            rejAreaMax = float(rejAreaPercent["Max"])

            rejAMSVal = int(rejByAMS["Val"])
            rejAMSMin = int(rejByAMS["Min"])
            rejAMSMax = int(rejByAMS["Max"])

            self.machineId = machineId
            self.stopWhenRejectCount = stopWhenRejectCount
            self.changeModeWhenProcessTrigCount = changeModeWhenProcessTrigCount
            self.maxProcessTimePerUnit = maxProcessTimePerUnit
            self.useAI = useAI
            self.inferenceRate = inferenceRate
            self.modeInspect = modeInspec
            self.useStopMachine = useStopMachine
            self.bboxCrop = {
                "R1" : R1,
                "C1" : C1,
                "R2" : R2,
                "C2" : C2,
            }
            self.processParameter = {
                "RejectByAMS" : {
                    "Val" : rejAMSVal,
                    "Min" : rejAMSMin,
                    "Max" : rejAMSMax
                },
                "RejectByPixelPercent" : {
                    "Val" : rejPixVal,
                    "Min" : rejPixMin,
                    "Max" : rejPixMax
                },
                "RejectByAreaPercent" : {
                    "Val" : rejAreaVal,
                    "Min" : rejAreaMin,
                    "Max" : rejAreaMax
                },
            }
            self.saveconfig()
            return True
        except Exception as ex:
            print('ERROR'+' Config format not correct !!! {}'.format(ex))
            return False
    
    def getCurrentConfig(self):
        return  {
                    "machineId" : self.machineId.strip(),
                    "stopWhenRejectCount" : int(self.stopWhenRejectCount),
                    "changeModeWhenProcessTrigCount" : int(self.changeModeWhenProcessTrigCount),
                    "maxProcessTimePerUnit" :int(self.maxProcessTimePerUnit),
                    "useAI" : self.useAI,
                    "inferenceRate" : self.inferenceRate,
                    "useStopMachine" : self.useStopMachine,
                    "bboxCrop" : self.bboxCrop,
                    "modeInspect" : self.modeInspect,
                    "processParameter" : self.processParameter,
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

# if __name__ == '__main__':
#     config = AIConfig()
    #config.loadConfig()
    # config.saveconfig()
    # print(config.getCurrentConfig())
    #Test Pass