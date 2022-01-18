from db_models.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class ListDose(Base):
    
    __tablename__ = "list_dose"
    
    dose_id = Column(Integer, primary_key=True)
    dose_name = Column(Integer)
    dose_name_api = Column(String) 
    
    vaccine_stat_dose = relationship("UkraineStatVaccine", backref="vaccine_stat_dose")
    
    def __init__(self, 
                 dose_id: int,
                 dose_name: str,
                 dose_name_api: str) -> None:
        
        self.dose_id = dose_id
        self.dose_name = dose_name
        self.dose_name_api = dose_name_api
        
    def __repr__(self) -> str:
        return f"ListDose(dose_id={self.dose_id}, dose_name={self.dose_name}, dose_name_api={self.dose_name_api})"
