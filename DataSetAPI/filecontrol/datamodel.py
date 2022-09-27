from enum import Enum
from pyexpat import model
from pydantic import BaseModel


class ImgMode (str, Enum):
    Process = "Process"
    SetupTrain = "SetupTrain"
    SetupTest = "SetupTest"
    Reject = "Reject"


class ImgModel(BaseModel):
    mode: ImgMode
    imgList: list

class ImgFile(BaseModel):
    mode: ImgMode
    imgfilename: str

class ImgCrop(BaseModel):
    mode: ImgMode
    imgfilename: str
    bbox: tuple