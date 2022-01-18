from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from utils.utils import get_environment_variable


covid_db_name = get_environment_variable("DATABASE_COVID_NAME")


engine = create_engine(f"sqlite:///{covid_db_name}")
Session = sessionmaker(bind=engine)
Base = declarative_base()

def create_database():
    Base.metadata.create_all(engine)