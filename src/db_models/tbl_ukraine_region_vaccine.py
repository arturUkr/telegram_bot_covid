from db_models.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey


class UkraineStatVaccine(Base):
    
    __tablename__ = "ukraine_region_vaccine"
    # ! PK
    ukraine_region_vaccine_id =  Column(Integer, primary_key=True, autoincrement=True)
    # ! FK
    report_date_id = Column(Integer, ForeignKey("list_report_date.report_date_id"))
    region_id = Column(Integer, ForeignKey("list_ukraine_region.region_id"))
    vaccine_id = Column(Integer, ForeignKey("list_vaccines.vaccine_id"))
    dose_id = Column(Integer, ForeignKey("list_dose.dose_id"))
    # ! fields
    count_vaccine = Column(Integer)
    count_vaccine_cum = Column(Integer)
        
    def __init__(self, 
                 report_date_id: int, 
                 region_id: int,
                 vaccine_id: int,
                 dose_id: int,
                 count_vaccine: int,
                 count_vaccine_cum: int) -> None:
        
        self.report_date_id = report_date_id
        self.region_id = region_id
        self.vaccine_id = vaccine_id
        self.dose_id = dose_id
        self.count_vaccine = count_vaccine
        self.count_vaccine_cum = count_vaccine_cum
        
    def __repr__(self) -> str:
        return f"ListVaccine(vaccine_id={self.vaccine_id}, vaccine_name={self.vaccine_name}, vaccine_name_api={self.vaccine_name_api})"
