from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class bbox(BaseModel):
    R1 :int = 194
    C1 :int = 279
    R2 :int = 290
    C2 :int = 377

class AITrainingLogModel(BaseModel):
    userTraining: str
    userLevel: str
    lotNo:str
    nImgTrain: int
    roiCropImg = bbox()
    startTrain: datetime
    finishTrain: datetime 
    remark: str = None
    class Config:
        schema_extra = {
            "example": {
                "userTraining":"123456 (Your EN)",
                "userLevel":"Engineer (Your Level)",
                "lotNo":"lotRun",
                "nImgTrain" : 25,
                "roiCropImg": {
                    "R1":194,
                    "C1":279,
                    "R2":290,
                    "C2":377
                },
                "startTrain": datetime.now(),
                "finishTrain": datetime.now(),
                "remark": "Note something"
            }
        }