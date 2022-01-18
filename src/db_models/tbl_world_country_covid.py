from sqlalchemy import Column, Integer, Float, ForeignKey
from db_models.database import Base
from typing import Optional, Union


class WorldStat(Base):
    
    __tablename__ = "world_country_covid"
    # ! PK
    world_country_covid_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    # ! FK
    country_id = Column(Integer, ForeignKey("list_country.country_id"))
    report_date_id  = Column(Integer, ForeignKey("list_report_date.report_date_id"))
    
    # ! fields - main (cumulative data)
    confirmed = Column(Float, nullable=True)
    deaths = Column(Float, nullable=True)
    recovered = Column(Float, nullable=True)
    existing = Column(Float, nullable=True)
    
    # ! fields calculated- main (daily data)
    confirmed_daily = Column(Float, nullable=True)
    deaths_daily = Column(Float, nullable=True)
    recovered_daily = Column(Float, nullable=True)
    existing_daily = Column(Float, nullable=True)
    confirmed_daily_percent = Column(Float, nullable=True)
    deaths_daily_percent = Column(Float, nullable=True)
    recovered_daily_percent = Column(Float, nullable=True)
    existing_daily_percent = Column(Float, nullable=True)
    
    def __init__(self, 
                 country_id: int,
                 report_date_id: int,
                 confirmed: Optional[Union[int, float]] = None,
                 deaths: Optional[Union[int, float]] = None, 
                 recovered: Optional[Union[int, float]] = None, 
                 existing: Optional[Union[int, float]] = None,
                 confirmed_daily: Optional[Union[int, float]] = None,
                 deaths_daily: Optional[Union[int, float]] = None, 
                 recovered_daily: Optional[Union[int, float]] = None, 
                 existing_daily: Optional[Union[int, float]] = None,
                 confirmed_daily_percent: Optional[Union[int, float]] = None,
                 deaths_daily_percent: Optional[Union[int, float]] = None, 
                 recovered_daily_percent: Optional[Union[int, float]] = None, 
                 existing_daily_percent: Optional[Union[int, float]] = None) -> None:
                 
        """
        existing - хворіє;
        recovered - одужало;
        deaths - померло;
        confirmed - виявлено;
        """         

        self.country_id = country_id
        self.report_date_id = report_date_id
        
        self.confirmed = float(confirmed)
        self.deaths = float(deaths)
        self.recovered = float(recovered)
        self.existing = float(existing)
        
        self.confirmed_daily = float(confirmed_daily)
        self.deaths_daily = float(deaths_daily)
        self.recovered_daily = float(recovered_daily)
        self.existing_daily = float(existing_daily)
        
        self.confirmed_daily_percent = float(confirmed_daily_percent)
        self.deaths_daily_percent = float(deaths_daily_percent)
        self.recovered_daily_percent = float(recovered_daily_percent)
        self.existing_daily_percent = float(existing_daily_percent)
        
    def __repr__(self) -> str:
        result = f"WorldStat(country_id={self.country_id}, report_date_id={self.report_date_id}, \
                 confirmed={self.confirmed}, deaths={self.deaths}, recovered={self.recovered}, existing={self.existing})"
        return result
