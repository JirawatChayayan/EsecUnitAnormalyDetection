from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class AITrainingLogModel(BaseModel):
    userTraining: str
    userLevel: str
    nImgTrain: int
    roiCropImg: list
    startTrain: datetime
    finishTrain: datetime 
    remark: str = None
    class Config:
        schema_extra = {
            "example": {
                "userTraining":"123456 (Your EN)",
                "userLevel":"Engineer (Your Level)",
                "nImgTrain" : 25,
                "roiCropImg": [0,0,100,100],
                "startTrain": datetime.now(),
                "finishTrain": datetime.now(),
                "remark": "Note something"
            }
        }