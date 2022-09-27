import sqlalchemy
from sqlalchemy.orm import sessionmaker

host="localhost"
user="root"
password= "root"#"admin"

engine = sqlalchemy.create_engine('mysql+pymysql://{}:{}@{}/esec_abnormally_db'.format(user, password, host),echo = False)
session = sessionmaker(bind = engine)

def get_db():
    try:
        db = session()
        yield db
    finally:
        db.close()
