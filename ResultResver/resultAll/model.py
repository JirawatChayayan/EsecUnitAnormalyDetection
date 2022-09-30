from datetime import datetime
from pydantic import BaseModel
from typing import List

class ImageResultAllModel(BaseModel):
    lotNo:str
    lotNoCount:int
    imgRawPath: str
    imgHeatMapPath: str
    scoreMin: int
    scoreMax: int

    defectPercent:float
    setupValue: float 
    processMode: int
    isReject:bool

    machineNo: str
    imgFileName: str
    class Config:
        schema_extra = {
            "example": {
                "lotNo":"PAPPK2199.1 (Lot No)",
                "lotNoCount":1,
                "imgRawPath":"path/to/file",
                "imgHeatMapPath":"path/to/file",
                "scoreMin": 0,
                "scoreMax": 255,
                "defectPercent": 5.00,
                "setupValue": 150.00,
                "processMode":1,
                "isReject":True,
                "machineNo": "ESEC-99P",
                "imgFileName": "file_name_with out extention (.png)"
            }
        }

class GetImageModel(BaseModel):
    item: int
    imgFileName: str
    createDate: datetime
    class Config:
        schema_extra = {
            "example": {
                "item": 0,
                "imgFileName":"file_name_with out extention (.png)",
                "createDate": datetime.now(),
            }
        }
