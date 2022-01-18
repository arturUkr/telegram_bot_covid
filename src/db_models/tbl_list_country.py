from typing import Optional
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db_models.database import Base
from db_models.tbl_world_country_covid import WorldStat


class Country(Base):
    __tablename__ = 'list_country'
    
    country_id = Column(Integer, primary_key=True)
    country_name = Column(String, nullable=False)
    country_name_flag = Column(String, nullable=True)
    # ! one-to-many relationship list_country.country_id -> world_country_covid.country_id
    world_stats = relationship("WorldStat", backref="list_country")
    
    def __init__(self,
                 country_id: int, 
                 country_name: str, 
                 country_name_flag: Optional[str] = None) -> None:
        """

        Args:
            country_id (int): country ID
            country_name (str): country name
            country_name_flag (str): short country name for create emoji country flag in telegram message 
        """
        self.country_id = country_id
        self.country_name = country_name
        self.country_name_flag = country_name_flag
    
    def __repr__(self) -> str:
        return f"Country(country_id={self.country_id}, country_name={self.country_name}, country_name_flag={self.country_name_flag})"