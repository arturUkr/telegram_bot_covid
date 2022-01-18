

from db_models.database import Session
from db_models import WorldStat, Country, ReportDate, ListRegion, UkraineStat, UkraineStatVaccine, ListDose, ListVaccine
from sqlalchemy import func
from typing import List, Optional, Tuple, Union
from typing import Any
import flag
import pandas as pd
import datetime
from loguru import logger
from utils.exceptions import ErrorSQLTableName


class CovidSQLGetterConfig:
    
    _TABLE_LIST = {
        "list_country": {"obj": Country},
        "list_report_date": {"obj": ReportDate},
        "list_dose": {"obj": ListDose},
        "list_vaccines": {"obj": ListVaccine},
        "world_country_covid": {"obj": WorldStat},
        "list_ukraine_region": {"obj": ListRegion},
        "ukraine_region_covid": {"obj": UkraineStat}
    }    
    
    
class CovidSQLGetter(CovidSQLGetterConfig):
    
    def __init__(self, session: Session) -> None:
        
        CovidSQLGetterConfig.__init__(self)
        
        self.session = session
    
    def get_covid_tbl_name (self) -> List[str]:
        return list(self._TABLE_LIST.keys())  
    
    @staticmethod
    def _object2dataframe(obj: Union[Any, List[Any]]) -> pd.DataFrame:
        """Convert object with value into pandas dataframe

        Args:
            obj (Union[Any, List[Any]]): object

        Returns:
            pd.DataFrame: pandas dataframe with data from input object.
        """
        obj = [obj] if not isinstance(obj, list) else obj
        result = []
        for o in obj:
            obj2dict = o.__dict__   # get attribute from object
            del obj2dict["_sa_instance_state"]   # delete information key
            result.append(obj2dict)
        return pd.DataFrame(result)
        
    def get_all_data_from_tbl(self, tbl_name: str, is_dataframe: bool = True) -> Union[pd.DataFrame, Country]:
        """Get all data from SQL table

        Args:
            tbl_name (str): SQL table name;
            is_dataframe (bool, optional): return result like pandas DataFrame. Defaults to True.

        Returns:
            Union[pd.DataFrame, Country]: all data from SQL table like list ob object or pandas dataframe.
        """
        if tbl_name not in self.get_covid_tbl_name():
            logger.opt(ansi=True).error(f"Input sql table name <green>{tbl_name}</green> doesn't exists (try: {self.get_covid_tbl_name()})")
            raise ErrorSQLTableName
            
        tbl_obj = self._TABLE_LIST[tbl_name]["obj"] 
        sql_query = self.session.query(tbl_obj) 
        result = sql_query.all()  
        self.session.close()

        if is_dataframe:
            result_df = []
            for obj_ in result:
                obj2dict = obj_.__dict__   # get attribute from object
                del obj2dict["_sa_instance_state"]   # delete information key
                result_df.append(obj2dict)
            return pd.DataFrame(result_df)

        return result
    
    def get_last_date(self) -> Tuple[int, datetime.date]:
        """Select last report date.

        Returns:
            int: ID for last date and date in sql table list_report_date
        """
        sql_last_date = self.session.query(func.max(ReportDate.report_date)).scalar_subquery()
        sql_last_date_id = self.session.query(ReportDate.report_date_id, ReportDate.report_date).filter(ReportDate.report_date == sql_last_date)
        result = sql_last_date_id.first()
        self.session.close()
        return result
     
    def get_world_stat(self, 
                       date_from: Optional[str] = None, 
                       date_to: Optional[str] = None) -> pd.DataFrame:
        
        sql_query = self.session.query(ReportDate.report_date,
                                       func.sum(WorldStat.confirmed_daily),
                                       func.sum(WorldStat.deaths_daily),
                                       func.sum(WorldStat.existing_daily),
                                       func.sum(WorldStat.recovered_daily)) \
            .join(ReportDate, WorldStat.report_date_id == ReportDate.report_date_id) \
            .group_by(ReportDate.report_date)
            
        if date_from is not None:
            sql_query = sql_query.filter(ReportDate.report_date >= date_from)
        
        if date_to is not None:
            sql_query = sql_query.filter(ReportDate.report_date <= date_to) 
                   
        result = pd.DataFrame(sql_query.all(), columns=["report_date", "confirmed_daily", "deaths_daily", "existing_daily", "recovered_daily"]) 
        
        result["report_date"] = pd.to_datetime(result["report_date"])
        
        # calculate percent dynamic lag 1
        for col_ in ["confirmed_daily", "deaths_daily", "existing_daily", "recovered_daily"]:
            result[f"{col_}_percent"] = result[col_].diff(periods=1) / result[col_].shift(periods=1)
        return result
                  
    def get_country_stat(self, 
                         date_from: Optional[str] = None, 
                         date_to: Optional[str] = None, 
                         is_last_date: bool = False,
                         country_name: Optional[Union[str, List[str]]] = None,
                         top_n: Optional[int] = None) -> pd.DataFrame:
        
        # start main query
        sql_query = self.session.query(WorldStat, 
                                       Country, 
                                       ReportDate) \
            .join(Country, WorldStat.country_id == Country.country_id) \
            .join(ReportDate, WorldStat.report_date_id == ReportDate.report_date_id)
        
        # filter by date
        if is_last_date:
           last_date_id, last_date = self.get_last_date()
           sql_query = sql_query.filter(ReportDate.report_date_id == last_date_id)
        elif date_from is not None:
            sql_query = sql_query.filter(ReportDate.report_date >= date_from)
        elif date_to is not None:
            sql_query = sql_query.filter(ReportDate.report_date <= date_to)
        
        # filter by country name
        if country_name is not None:
            country_name = country_name if isinstance(country_name, list) else [country_name]
            sql_query = sql_query.filter(Country.country_name.in_(country_name))
            
        # sort by confirmed value descent and select TOP n
        if top_n is not None:
            sql_query = sql_query.order_by(WorldStat.confirmed_daily.desc()).limit(top_n)
         
        # finish - get data   
        result = sql_query.all()
        self.session.close()
        
        # prepare query result like pandas dataframe
        result_df = []
        for res_ in result:
            result_df.append(
                {
                    "country_name": res_.Country.country_name,
                    "country_name_flag": res_.Country.country_name_flag,
                    "report_date": res_.ReportDate.report_date,
                    # виявлено
                    "confirmed": res_.WorldStat.confirmed,
                    "confirmed_daily": res_.WorldStat.confirmed_daily,
                    "confirmed_daily_percent": res_.WorldStat.confirmed_daily_percent,
                    # померло
                    "deaths": res_.WorldStat.deaths,  
                    "deaths_daily": res_.WorldStat.deaths_daily,
                    "deaths_daily_percent": res_.WorldStat.deaths_daily_percent,
                    # одужало
                    "recovered": res_.WorldStat.recovered,  
                    "recovered_daily": res_.WorldStat.recovered_daily,
                    "recovered_daily_percent": res_.WorldStat.recovered_daily_percent,
                    # хворіє
                    "existing": res_.WorldStat.existing,  
                    "existing_daily": res_.WorldStat.existing_daily,
                    "existing_daily_percent": res_.WorldStat.existing_daily_percent
                }                
            )
        result_df = pd.DataFrame(result_df)
        return result_df

    def get_ukraine_stat(self, 
                         date_from: Optional[str] = None, 
                         date_to: Optional[str] = None, 
                         is_last_date: bool = False,
                         region_name: Optional[Union[str, List[str]]] = None,
                         top_n: Optional[int] = None) -> pd.DataFrame:
        
        # start main query
        sql_query = self.session.query(UkraineStat, 
                                       ListRegion, 
                                       ReportDate) \
            .join(ListRegion, UkraineStat.region_id == ListRegion.region_id) \
            .join(ReportDate, UkraineStat.report_date_id == ReportDate.report_date_id)
        
        # filter by date
        if is_last_date:
           last_date_id, last_date = self.get_last_date()
           sql_query = sql_query.filter(ReportDate.report_date_id == last_date_id)
        elif date_from is not None:
            sql_query = sql_query.filter(ReportDate.report_date >= date_from)
        elif date_to is not None:
            sql_query = sql_query.filter(ReportDate.report_date <= date_to)      
        
        # filter by region name
        if region_name is not None:
            region_name = region_name if isinstance(region_name, list) else [region_name]
            sql_query = sql_query.filter(ListRegion.region_name.in_(region_name))
            
        # sort by confirmed value descent and select TOP n
        if top_n is not None:
            sql_query = sql_query.order_by(UkraineStat.confirmed_daily.desc()).limit(top_n)  
         
        # finish - get data   
        result = sql_query.all()
        self.session.close()
        
        # prepare query result like pandas dataframe
        result_df = []
        for res_ in result:
            result_df.append(
                {
                    "region_name": res_.ListRegion.region_name,
                    "report_date": res_.ReportDate.report_date,
                    # виявлено
                    "confirmed": res_.UkraineStat.confirmed,
                    "confirmed_daily": res_.UkraineStat.confirmed_daily,
                    "confirmed_daily_percent": res_.UkraineStat.confirmed_daily_percent,
                    # померло
                    "deaths": res_.UkraineStat.deaths,  
                    "deaths_daily": res_.UkraineStat.deaths_daily,
                    "deaths_daily_percent": res_.UkraineStat.deaths_daily_percent,
                    # одужало
                    "recovered": res_.UkraineStat.recovered,  
                    "recovered_daily": res_.UkraineStat.recovered_daily,
                    "recovered_daily_percent": res_.UkraineStat.recovered_daily_percent,
                    # хворіє
                    "existing": res_.UkraineStat.existing,  
                    "existing_daily": res_.UkraineStat.existing_daily,
                    "existing_daily_percent": res_.UkraineStat.existing_daily_percent
                }                
            )
        result_df = pd.DataFrame(result_df)
        return result_df            
    
    def get_ukraine_agg_stat(self, 
                            date_from: Optional[str] = None, 
                            date_to: Optional[str] = None) -> pd.DataFrame:
        
        sql_query = self.session.query(ReportDate.report_date,
                                       func.sum(UkraineStat.confirmed_daily),
                                       func.sum(UkraineStat.deaths_daily),
                                       func.sum(UkraineStat.recovered_daily),
                                       func.sum(UkraineStat.existing_daily)) \
            .join(ReportDate, UkraineStat.report_date_id == ReportDate.report_date_id) \
            .group_by(ReportDate.report_date)
            
        if date_from is not None:
            sql_query = sql_query.filter(ReportDate.report_date >= date_from)
        
        if date_to is not None:
            sql_query = sql_query.filter(ReportDate.report_date <= date_to) 
                   
        result = pd.DataFrame(sql_query.all(), columns=["report_date", "confirmed_daily", "deaths_daily", "existing_daily", "recovered_daily"]) 
        
        result["report_date"] = pd.to_datetime(result["report_date"])
        
        # calculate percent dynamic lag 1
        for col_ in ["confirmed_daily", "deaths_daily", "existing_daily", "recovered_daily"]:
            result[f"{col_}_percent"] = result[col_].diff(periods=1) / result[col_].shift(periods=1)
        
        self.session.close()
        return result
        
            
    def get_vaccine_agg_stat(self, 
                            date_from: Optional[str] = None, 
                            date_to: Optional[str] = None ) -> pd.DataFrame:
        
        sql_query = self.session.query(ReportDate.report_date,
                                       func.sum(UkraineStatVaccine.count_vaccine)) \
            .join(ReportDate, ReportDate.report_date_id == UkraineStatVaccine.report_date_id) \
            .group_by(ReportDate.report_date)
            
        if date_from is not None:
            sql_query = sql_query.filter(ReportDate.report_date >= date_from)
        
        if date_to is not None:
            sql_query = sql_query.filter(ReportDate.report_date <= date_to) 
                   
        result = pd.DataFrame(sql_query.all(), columns=["report_date", "count_vaccine_daily"]) 
        # calculate percent dynamic lag 1
        for col_ in ["count_vaccine_daily"]:
            result[f"{col_}_percent"] = result[col_].diff(periods=1) / result[col_].shift(periods=1)
        
        self.session.close()
        return result
        
        
        
            
    def get_vaccine_stat(self, 
                         date_from: Optional[str] = None, 
                         date_to: Optional[str] = None, 
                         is_last_date: bool = False,
                         region_name: Optional[Union[str, List[str]]] = None,
                         dose_name: Optional[Union[int, List[int]]] = None,
                         top_n: Optional[int] = None) -> pd.DataFrame:
        
        # start main query
        sql_query = self.session.query(UkraineStatVaccine, 
                                       ListRegion, 
                                       ReportDate,
                                       ListVaccine,
                                       ListDose) \
            .join(ListRegion, UkraineStatVaccine.region_id == ListRegion.region_id) \
            .join(ReportDate, UkraineStatVaccine.report_date_id == ReportDate.report_date_id) \
            .join(ListVaccine, UkraineStatVaccine.vaccine_id == ListVaccine.vaccine_id) \
            .join(ListDose, UkraineStatVaccine.dose_id == ListDose.dose_id)
        
        # filter by date
        if is_last_date:
           last_date_id, last_date = self.get_last_date()
           sql_query = sql_query.filter(ReportDate.report_date_id == last_date_id)
        elif date_from is not None:
            sql_query = sql_query.filter(ReportDate.report_date >= date_from)
        elif date_to is not None:
            sql_query = sql_query.filter(ReportDate.report_date <= date_to)      
        
        # filter by region name
        if region_name is not None:
            region_name = region_name if isinstance(region_name, list) else [region_name]
            sql_query = sql_query.filter(ListRegion.region_name.in_(region_name))
        
        if dose_name is not None:
            dose_name = dose_name if isinstance(dose_name, list) else [dose_name]
            sql_query = sql_query.filter(ListDose.dose_name.in_(dose_name))
            
        # sort by confirmed value descent and select TOP n
        if top_n is not None:
            sql_query = sql_query.order_by(UkraineStatVaccine.count_vaccine.desc()).limit(top_n)  
         
        # finish - get data   
        result = sql_query.all()
        self.session.close()
       
        # prepare query result like pandas dataframe
        result_df = []
        for res_ in result:
            result_df.append(
                {
                    "region_name": res_.ListRegion.region_name,
                    "report_date": res_.ReportDate.report_date,
                    "vaccine_name": res_.ListVaccine.vaccine_name,
                    "dose_name": res_.ListDose.dose_name,
                    # кількість вакцин
                    "count_vaccine": res_.UkraineStatVaccine.count_vaccine,
                    "count_vaccine_cum": res_.UkraineStatVaccine.count_vaccine_cum 
                }                
            )
        result_df = pd.DataFrame(result_df)
        self.session.close()
        return result_df   
    

