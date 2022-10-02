
from tkinter.tix import INTEGER
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, LargeBinary,Float
from sqlalchemy.dialects.mysql import LONGTEXT
from pydantic.datetime_parse import datetime
from db.db import engine
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class REJECT_RESULT(Base):
    __tablename__ = 'anormaly_result'
    ITEM = Column(Integer, primary_key=True, index=True)
    
    LOT_NO = Column(String(100))
    LOT_NO_COUNT = Column(Integer)
    FILENAME = Column(String(50))

    IMG_RAW = Column(LONGTEXT)
    IMG_HEATMAP = Column(LONGTEXT)

    SCORE_MIN = Column(Integer)
    SCORE_MAX = Column(Integer)

    DEFECT_PERCENT = Column(Float)
    SETUP_VALUE = Column(Float)
    PROCESS_MODE = Column(Integer)

    MACHINE_NO = Column(String(50))
    CREATEDATE = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    ACTIVEFLAG = Column(Boolean, default=True)

class ALL_RESULT(Base):
    __tablename__ = 'anormaly_all_result'
    ITEM = Column(Integer, primary_key=True, index=True)
    
    LOT_NO = Column(String(100))
    LOT_NO_COUNT = Column(Integer)
    FILENAME = Column(String(50))

    IMG_RAW_PATH = Column(String(300))
    IMG_HEATMAP_PATH = Column(String(300))

    SCORE_MIN = Column(Integer)
    SCORE_MAX = Column(Integer)

    DEFECT_PERCENT = Column(Float)
    SETUP_VALUE = Column(Float)
    PROCESS_MODE = Column(Integer)
    IS_REJECT = Column(Boolean)

    MACHINE_NO = Column(String(50))
    CREATEDATE = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    ACTIVEFLAG = Column(Boolean, default=True)

class TEST_RESULT(Base):
    __tablename__ = 'anormaly_test_result'
    ITEM = Column(Integer, primary_key=True, index=True)
    
    LOT_NO = Column(String(100))
    LOT_NO_COUNT = Column(Integer)
    FILENAME = Column(String(50))

    IMG_RAW_PATH = Column(String(300))
    IMG_HEATMAP_PATH = Column(String(300))

    SCORE_MIN = Column(Integer)
    SCORE_MAX = Column(Integer)

    DEFECT_PERCENT = Column(Float)
    SETUP_VALUE = Column(Float)
    PROCESS_MODE = Column(Integer)
    IS_REJECT = Column(Boolean)

    MACHINE_NO = Column(String(50))
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
    LOT_NO = Column(String(50))
    LOT_NO_COUNT = Column(Integer)
    TRAINER = Column(String(50))
    TRAINER_LEVEL = Column(String(50))
    TRAINING_IMAGE = Column(Integer)
    TRAINING_ROI = Column(String(800))
    TRAINING_START = Column(TIMESTAMP(timezone=False))
    TRAINING_FINISH = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
    REMARK = Column(String(5000))
    ACTIVEFLAG = Column(Boolean, default=True)

Base.metadata.create_all(engine)