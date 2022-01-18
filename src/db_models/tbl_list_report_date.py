from sqlalchemy import Column, Integer, Date
from sqlalchemy.orm import relationship
from db_models.database import Base
import datetime

class ReportDate(Base):
    
    __tablename__ = "list_report_date"
    
    report_date_id = Column(Integer, primary_key=True, nullable=False)
    report_date = Column(Date, nullable=False)
    is_lockdown_ukraine = Column(Integer, nullable=True)
    # ! one-to-many relationship list_report_date.report_date_id -> world_country_covid.report_date_id
    world_stats = relationship("WorldStat", backref="list_report_date")
    ukraine_stats = relationship("UkraineStat", backref="list_report_date_ukraine")
    vaccine_stat_date = relationship("UkraineStatVaccine", backref="vaccine_stat_date")

    def __init__(self, 
                 report_date_id: int, 
                 report_date: datetime.date, 
                 is_lockdown_ukraine: int) -> None:
        """[summary]

        Args:
            report_date_id (int): date ID
            report_date (datetime.date): date value
            is_lockdown_ukraine (int): 1 - was lockdown in Ukraine, else - 0
        """
        self.report_date_id = report_date_id
        self.report_date = report_date
        self.is_lockdown_ukraine = is_lockdown_ukraine
        
    def __repr__(self) -> str:
        return f"ReportDate(report_date_id={self.report_date_id}, report_date={self.report_date}, is_lockdown_ukraine={self.is_lockdown_ukraine})"
