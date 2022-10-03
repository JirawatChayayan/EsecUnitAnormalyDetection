
from pydantic import BaseModel

class controlParameter(BaseModel):
    Val:float = 5.00
    Min:float = 1.00
    Max:float = 5.00


class controlParameterInt(BaseModel):
    Val:int = 150
    Min:int = 100
    Max:int = 180

class processParameter(BaseModel):
    RejectByPixelPercent:controlParameter = controlParameter()
    RejectByAreaPercent:controlParameter = controlParameter()
    RejectByAMS:controlParameterInt = controlParameterInt()


class ConfigModel(BaseModel):
    machineId : str = 'ESEC2008-01P'
    stopWhenRejectCount:int = 1
    changeModeWhenProcessTrigCount:int = 20 
    maxProcessTimePerUnit:int = 1
    useAI:bool = False
    inferenceRate:int = 5
    modeInspect:int = 1
    useStopMachine:bool = False

class bbox(BaseModel):
    R1 :int = 194
    C1 :int = 279
    R2 :int = 290
    C2 :int = 377