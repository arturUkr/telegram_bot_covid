from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#from utils.utils import get_environment_variable
from utils.config import Config


engine = create_engine(f"sqlite:///{Config.DATABASE_COVID_NAME}")
Session = sessionmaker(bind=engine)
Base = declarative_base()

def create_database():
    Base.metadata.create_all(engine)
