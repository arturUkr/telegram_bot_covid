from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db_models.database import Base


class ListRegion(Base):
    
    __tablename__ = "list_ukraine_region"
    
    region_id = Column(Integer, primary_key=True)
    region_covid_id = Column(Integer)
    region_vaccines_id = Column(Integer)
    region_name = Column(String)
    ukraine_stats = relationship("UkraineStat", backref="ukraine_stats")
    vaccine_stat_region = relationship("UkraineStatVaccine", backref="vaccine_stat_region")
    
    def __init__(self, region_id, region_covid_id, region_vaccines_id, region_name):
        
        self.region_id = region_id
        self.region_covid_id = region_covid_id
        self.region_vaccines_id = region_vaccines_id
        self.region_name = region_name

    def __repr__(self) -> str:
        return f"Region(region_id={self.region_id}, \
            region_covid_id={self.region_covid_id},  \
            region_vaccines_id={self.region_vaccines_id}, \
            region_name={self.region_name})"
