from db_models.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class ListVaccine(Base):
    
    __tablename__ = "list_vaccines"
    
    vaccine_id = Column(Integer, primary_key=True)
    vaccine_name = Column(Integer)
    vaccine_name_api = Column(String) 
    vaccine_stat = relationship("UkraineStatVaccine", backref="vaccine_stat")

    
    def __init__(self, vaccine_id: int, vaccine_name: str, vaccine_name_api: str) -> None:
        self.vaccine_id = vaccine_id
        self.vaccine_name = vaccine_name
        self.vaccine_name_api = vaccine_name_api
        
    def __repr__(self) -> str:
        return f"ListVaccine(vaccine_id={self.vaccine_id}, vaccine_name={self.vaccine_name}, vaccine_name_api={self.vaccine_name_api})"
