from datetime import datetime
from pydantic import BaseModel
from typing import List

class ImageResultModel(BaseModel):
    imgRaw: str
    imgHeatMap: str
    scoreMin: int
    scoreMax: int
    rejectThreshold: int 
    machineNo: str
    imgFileName: str
    class Config:
        schema_extra = {
            "example": {
                "imgRaw":"data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAB34AAAQeCAYA.....",
                "imgHeatMap":"data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAB34AAAQeCAYA.....",
                "scoreMin": 0,
                "scoreMax": 255,
                "rejectThreshold": 150,
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


class ImageResultModels(BaseModel):
    dataItem: List[ImageResultModel]
   