
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, LargeBinary
from sqlalchemy.dialects.mysql import LONGTEXT
from pydantic.datetime_parse import datetime
from db.db import engine
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class REJECT_RESULT(Base):
    __tablename__ = 'anormaly_result'
    ITEM = Column(Integer, primary_key=True, index=True)
    IMG_RAW = Column(LONGTEXT)
    IMG_HEATMAP = Column(LONGTEXT)
    # IMG_TYPE = Column(String(50))
    SCORE_MIN = Column(Integer)
    SCORE_MAX = Column(Integer)
    MACHINE_NO = Column(String(50))
    FILENAME = Column(String(50))
    REJECT_THRESHOLD = Column(Integer)
    CREATEDATE = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    ACTIVEFLAG = Column(Boolean, default=True)

class MC_LOG(Base):
    __tablename__ = 'stop_release_mc_log'
    ITEM = Column(Integer, primary_key=True, index=True)
    TIMESTAMP = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    REMARK = Column(String(5000))
    ACTIVEFLAG = Column(Boolean, default=True)


class AITrainingLog(Base):
    __tablename__ = 'ai_training_log'
    ITEM = Column(Integer, primary_key=True, index=True)
    TRAINER = Column(String(50))
    TRAINER_LEVEL = Column(String(50))
    TRAINING_IMAGE = Column(Integer)
    TRAINING_ROI = Column(String(800))
    TRAINING_START = Column(TIMESTAMP(timezone=False))
    TRAINING_FINISH = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    REMARK = Column(String(5000))
    ACTIVEFLAG = Column(Boolean, default=True)

 

Base.metadata.create_all(engine)