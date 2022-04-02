from enum import Enum
from pyexpat import model
from pydantic import BaseModel


class ImgMode (str, Enum):
    Process = "Process"
    SetupTrain = "SetupTrain"
    SetupTest = "SetupTest"


class ImgModel(BaseModel):
    mode: ImgMode
    imgList: list