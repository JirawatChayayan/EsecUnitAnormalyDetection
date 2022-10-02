from pydantic import BaseModel

class bbox(BaseModel):
    R1 :int = 194
    C1 :int = 279
    R2 :int = 290
    C2 :int = 377

class TrainingModel(BaseModel):
    imgList:list = []
    bbox = bbox()

class InferModel(BaseModel):
    imgList:list =None
    bbox = bbox()
    anomalyThreshold : int = None
    procMode : int = None 
    controlValue : float = None
    showAllImage : bool = True

class InferModelMonitor(BaseModel):
    imgList:list =None
    bbox = bbox()
    anomalyThreshold : int = None
    procMode : int = None 
    controlValueProc1 : float = None
    controlValueProc2 : float = None
    controlValueProc3 : float = None
    showAllImage : bool = True

class MatData(BaseModel):
    img: str
    bbox = bbox()


