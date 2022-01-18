from db_models import WorldStat, ListOperations, ListRegion, Country, ReportDate, DBLogger, UkraineStat, ListDose, ListVaccine, UkraineStatVaccine
from db_models import add_operations, add_sql_log
from db_models.database import Session, create_database, Base
from utils.exceptions import ErrorBadApiResponse
from utils.config import Config

from typing import Any, Optional, Union, List
from loguru import logger
import sqlalchemy as sa
import pandas as pd
import numpy as np
import datetime
import os
import json
import requests
import time
import itertools



class CovidDataFrameLoader:

    COVID_WORLD_BASE_URL = "https://api-covid19.rnbo.gov.ua/charts/main-data?mode=world"
    COVID_WORLD_COUNTRY_BASE_URL = "https://api-covid19.rnbo.gov.ua/charts/main-data?mode=world&country="    
    COVID_UKRAINE_REGION_BASE_URL = "https://api-covid19.rnbo.gov.ua/charts/main-data?mode=ukraine&country=" 
    
    START_DATE = datetime.date(year=2020, month=1, day=22)
    
    FILE_NAME_COUNTRY = "src/db_models/covid/data/list_country.json"
    FILE_NAME_REGION = "src/db_models/covid/data/list_ukraine_regions.json"
    FILE_NAME_DOSE = "src/db_models/covid/data/list_dose.json"
    FILE_NAME_VACCINE = "src/db_models/covid/data/list_vaccine.json"
       
    def __init__(self, 
                 country: Optional[Union[str, List[str]]] = "all", 
                 regions: Optional[Union[str, List[str]]] = "all") -> None:
        
        self.country = country
        self.regions = regions
        
        self._list_country_df = None
        self._list_date_df = None
        self._list_regions_df = None
        self._list_dose_df = None
        self._list_vaccines_df = None
        
    @property
    def list_country_df(self):
        return self._list_country_df.copy()

    @property
    def list_date_df(self):
        return self._list_date_df.copy()

    @property
    def list_region_df(self):
        return self._list_regions_df.copy()
    
    @staticmethod
    def _calculate_daily_data(data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        #data.replace(to_replace=0, value=np.nan, inplace=True)
        for col in ["confirmed", "deaths", "recovered", "existing"]:
            data[f"{col}_daily"] = data[col].diff()
            data[f"{col}_daily_percent"] = \
                (data[f"{col}_daily"] - data[f"{col}_daily"].shift()) / data[f"{col}_daily"].shift()
        #data.replace(to_replace=0, value=np.nan, inplace=True)
        return data  

    def _prepare_world_stat_data(self, data: pd.DataFrame) -> pd.DataFrame:
        
        # prepare report_date column for merge, must be type(list_date_report.report_date) == type(world_stat.report_date)   
        data = data.copy()
        data["report_date"] = pd.to_datetime(data["report_date"], format="%Y-%m-%d")
        data["report_date"] = data["report_date"].dt.date

        # add country ID by country Name
        data = data \
            .merge(self._list_country_df.loc[:, ["country_name", "country_id"]], how="inner", on="country_name") \
            .merge(self._list_date_df.loc[:, ["report_date", "report_date_id"]], how="inner", on="report_date") \
            .drop(columns=["report_date", "country_name"])        
       
        return data

    def _prepare_input_country(self) -> List:
        
        if self.country == "all":
            return self._list_country_df.loc[:, "country_name"].to_list()
        elif self.country is None or isinstance(self.country, str):
            return [self.country]
        else:
            return self.country

    def _prepare_input_region(self) -> List:
        
        if self.regions == "all":
            return self._list_regions_df.loc[:, "region_name"].to_list()
        elif self.regions is None or isinstance(self.regions, str):
            return [self.regions]
        else:
            return self.regions

    def create_list_report_date(self) -> pd.DataFrame:
        
        end_date = datetime.date.today()
        count_days = (end_date - CovidDataFrameLoader.START_DATE).days
        date_sequence = [CovidDataFrameLoader.START_DATE + datetime.timedelta(days=day_) for day_ in range(count_days)]

        result = pd.DataFrame({
            "report_date_id": list(range(1, count_days + 1)),
            "report_date": date_sequence,
            "is_lockdown_ukraine": [None] * count_days
        })
        # ! save date data for merge with world statistics
        self._list_date_df = result   
        logger.opt(ansi=True).debug(f"SQL Table <green>list_report_date</green> : <green>CREATED</green> dataframe for date_report, #rows-{result.shape[0]}, #cols-{result.shape[1]}")
        return result                        

    def create_list_country(self) -> pd.DataFrame:
        
        with open(CovidDataFrameLoader.FILE_NAME_COUNTRY) as f:
            result = json.load(f)
        result = pd.DataFrame(result)
        self._list_country_df = result   # ! save country list for merge with world statistics
        
        logger.opt(ansi=True).debug(f"SQL Table <green>list_country</green>: <green>CREATE</green> dataframe, #rows-{result.shape[0]}, #cols-{result.shape[1]}")
        return result

    def create_list_ukraine_region(self) -> pd.DataFrame:
        with open(CovidDataFrameLoader.FILE_NAME_REGION, encoding='utf-8') as f:
            result = json.load(f)
        result = pd.DataFrame(result)
        self._list_regions_df = result   # ! save Ukraine regions list for merge with ukraine statistics
        
        logger.opt(ansi=True).debug(f"SQL Table <green>list_ukraine_region</green>: <green>CREATE</green> dataframe, #rows-{result.shape[0]}, #cols-{result.shape[1]}")
        return result
    
    def create_list_dose(self) -> pd.DataFrame:
        with open(CovidDataFrameLoader.FILE_NAME_DOSE, encoding='utf-8') as f:
            result = json.load(f)
        result = pd.DataFrame(result)
        self._list_dose_df = result   # ! save DOSE list for merge with vaccine statistics
        
        logger.opt(ansi=True).debug(f"SQL Table <green>list_dose</green>: <green>CREATE</green> dataframe, #rows-{result.shape[0]}, #cols-{result.shape[1]}")
        return result
    
    def create_list_vaccine(self) -> pd.DataFrame:
        with open(CovidDataFrameLoader.FILE_NAME_VACCINE, encoding='utf-8') as f:
            result = json.load(f)
        result = pd.DataFrame(result)
        self._list_vaccines_df = result   # ! save VACCINE list for merge with vaccine statistics
        
        logger.opt(ansi=True).debug(f"SQL Table <green>list_vaccines</green>: <green>CREATE</green> dataframe, #rows-{result.shape[0]}, #cols-{result.shape[1]}")
        return result

    def _create_api_url_for_vaccine(self) -> List[str]:
        
        # generate combinations with dose number and region id for vaccine data
        regions: list = self._prepare_input_region()
        api_url_params = itertools.product(
            self._list_dose_df["dose_name_api"], 
            self._list_regions_df.query("region_name == @regions")["region_vaccines_id"]
        )
        # create api url for regions and dose number
        api_url = []
        for params_ in api_url_params:
            api_url.append(
                (params_[0], 
                 params_[1], 
                 f"https://health-security.rnbo.gov.ua/api/vaccination/process/chart?vaccines=&dose={params_[0]}&distributionBy=vaccine&regionId={params_[1]}")    
            )
        
        return api_url
                   
    def create_world_country_covid(self) -> pd.DataFrame:
        """Get covid statistics for countries from API.

        Raises:
            ErrorBadApiResponse: if API response status != 200.

        Returns:
            pd.DataFrame: covid statistics for countries from API
        """
        # convert all country to list, even it's str or None 
        country_list = self._prepare_input_country()
            
        result_country_list = []
        
        try:
            for iteration, country in enumerate(country_list):
                         
                # create api url string
                if country is not None and country != "":
                    api_url = self.COVID_WORLD_COUNTRY_BASE_URL + country
                else:
                    api_url = self.COVID_WORLD_BASE_URL 
                    country = "World"
                
                api_response = requests.get(api_url)   # ! get data for country from API
                
                if api_response.status_code != 200:
                    logger.error(f"Response for {api_url} = {api_response.status_code}, not 200")
                    raise ErrorBadApiResponse(f"Response for {api_url} = {api_response.status_code}, not 200")
                else:
                    # prepare api json respose to pandas dataframe, add country name, rename dates column
                    result = pd.DataFrame(api_response.json()) \
                        .rename(columns={"dates": "report_date"}) \
                        .assign(country_name=country) 

                    result = CovidDataFrameLoader._calculate_daily_data(data=result)   # ! calculate daily data from cumulative
                    result_country_list.append(result)
                    
                    logger.opt(ansi=True).debug(f"SQL Table <green>world_country_covid</green>: data for country ({iteration}) <green>{country}</green> created")     
                    time.sleep(1)
                                   
        except TimeoutError:
            logger.warning(f"TimeoutError for api url {api_url}")
            
        finally:
            if result_country_list:
                result_country_df = pd.concat(result_country_list, ignore_index=True)
                result_country_df = self._prepare_world_stat_data(result_country_df)
                    
                logger.opt(ansi=True).debug(f"SQL Table <green>world_country_covid</green>: \
                                            CREATE dataframe for  <green>ALL</green>, \
                                            #rows-{result_country_df.shape[0]}, #cols-{result_country_df.shape[1]}")
                return result_country_df 
    
    def create_ukraine_region_covid(self) -> pd.DataFrame:
        
        # convert all regions to list, even it's str or None 
        region_list = self._prepare_input_region()
        region_list = self._list_regions_df.loc[self._list_regions_df["region_name"].isin(region_list)].copy()
        
        result_region_list = []
        
        try:
            for iteration, region in enumerate(region_list.loc[:, "region_covid_id"].to_list()):         
                # create api url string
                if region is not None and region != "":
                    api_url = self.COVID_UKRAINE_REGION_BASE_URL + str(region)
                else:
                    api_url = self.COVID_UKRAINE_REGION_BASE_URL 
                    region = "Ukraine"
                            
                api_response = requests.get(api_url)           
                
                if api_response.status_code != 200:
                    logger.error(f"Response for {api_url} = {api_response.status_code}, not 200")
                    raise ErrorBadApiResponse(f"Response for {api_url} = {api_response.status_code}, not 200")
                else:
                    # prepare api json respose to pandas dataframe, add region id, rename dates column
                    result = pd.DataFrame(api_response.json()) \
                        .rename(columns={"dates": "report_date"}) \
                        .assign(region_id=int(region_list.loc[region_list["region_covid_id"] == region, "region_id"])) 
                    
                    result = CovidDataFrameLoader._calculate_daily_data(data=result)   # ! calculate daily data from cumulative data
                    result_region_list.append(result)
                    
                    region_name = str(region_list.loc[region_list["region_covid_id"] == region, "region_name"].to_list()[0])
                    logger.opt(ansi=True).debug(f"SQL Table <green>ukraine_region_covid</green>: data for region ({iteration}) <green>{region_name}</green> created")     
                    time.sleep(1) 
                    
        except TimeoutError:
            logger.warning(f"TimeoutError for api url {api_url}")
        
        finally:
            if result_region_list:              
                result_region_df = pd.concat(result_region_list, ignore_index=True)
                result_region_df["report_date"] = pd.to_datetime(result_region_df["report_date"], format="%Y-%m-%d")
                result_region_df["report_date"] = result_region_df["report_date"].dt.date
                
                # add date ID by report_date
                result_region_df = result_region_df \
                    .merge(self._list_date_df.loc[:, ["report_date", "report_date_id"]], how="inner", on="report_date") \
                    .drop(columns=["report_date"]) \
                    .sort_values(by=["region_id", "report_date_id"])
                            
                logger.opt(ansi=True).debug(f"SQL Table <green>ukraine_region_covid</green>: \
                                            CREATE dataframe for <green>ALL</green>, \
                                            #rows-{result_region_df.shape[0]}, #cols-{result_region_df.shape[1]}")
                return result_region_df                                 
    
    def create_ukraine_region_vaccine(self) -> pd.DataFrame:
        
        result_region_list = []
        try:
            for iteration, (dose_, region_, api_url_) in enumerate(self._create_api_url_for_vaccine()):

                api_response = requests.get(api_url_)           
                
                if api_response.status_code != 200:
                    logger.error(f"Response for {api_url_} = {api_response.status_code}, not 200")
                    raise ErrorBadApiResponse(f"Response for {api_url_} = {api_response.status_code}, not 200")
                else:  
                    res = api_response.json().get('daily')       
                    result = pd.concat([pd.DataFrame(res['dates']), pd.DataFrame(res['quantity'])], axis=1)
                    result = result.rename(columns={0: "report_date"})    
                    result = result.melt(id_vars="report_date", var_name="vaccine_name", value_name="count_vaccine")
                    result = result.assign(dose_name_api=dose_, region_vaccines_id=region_)
                    
                    result_region_list.append(result)
                    
                    region_name = str(self._list_regions_df.query("region_vaccines_id == @region_")["region_name"].to_list()[0])
                    logger.opt(ansi=True).debug(f"SQL Table <green>ukraine_region_vaccine</green>: data for region ({iteration}) <green>{region_name}</green> created")
        
        except TimeoutError:
            logger.warning(f"TimeoutError for api url {api_url_}")
        
        finally:
            if result_region_list:
                result_region_df = pd.concat(result_region_list, ignore_index=True)
                result_region_df["report_date"] = pd.to_datetime(result_region_df["report_date"], format="%Y-%m-%d")
                result_region_df["report_date"] = result_region_df["report_date"].dt.date 
                result_region_df = result_region_df \
                    .merge(self._list_date_df.loc[:, ["report_date", "report_date_id"]], how="inner", on="report_date") \
                    .merge(self._list_regions_df.loc[:, ["region_vaccines_id", "region_id"]], how="inner", on="region_vaccines_id") \
                    .merge(self._list_dose_df.loc[:, ["dose_name_api", "dose_id"]], how="inner", on="dose_name_api") \
                    .merge(self._list_vaccines_df.loc[:, ["vaccine_name", "vaccine_id"]], how="inner", on="vaccine_name") \
                    .drop(columns=["report_date", "region_vaccines_id", "dose_name_api", "vaccine_name"])
                
                result_region_df["count_vaccine_cum"] = result_region_df \
                    .groupby(by=["region_id", "vaccine_id", "dose_id"])["count_vaccine"] \
                    .transform('cumsum')
                                        
                logger.opt(ansi=True).debug(f"SQL Table <green>ukraine_region_vaccine</green>: CREATE dataframe for <green>ALL</green>, \
                                            #rows-{result_region_df.shape[0]}, \
                                            #cols-{result_region_df.shape[1]}")
                return result_region_df
        
                   
class CovidSQLSaver(CovidDataFrameLoader):
    
    def __init__(self, 
                 session: Session,
                 country: Optional[Union[str, List[str]]] = "all", 
                 regions: Optional[Union[str, List[str]]] = "all") -> None:
        """Class for save covid data into sql.

        Args:
            session (Session): sqlalchemy session;
            country (Optional[Union[str, List[str]]], optional): country(ies) we want to save. Defaults to "all".
            regions (Optional[Union[str, List[str]]], optional): Ukraine region(s) we want to save. Defaults to "all".
        """
        CovidDataFrameLoader.__init__(self, country=country, regions=regions)
        self.session = session
        self.TABLE_LIST = {
            "list_country": {"obj": Country, "create": self.create_list_country},
            "list_report_date": {"obj": ReportDate, "create": self.create_list_report_date},
            "list_ukraine_region": {"obj": ListRegion, "create": self.create_list_ukraine_region},
            "list_dose": {"obj": ListDose, "create": self.create_list_dose},
            "list_vaccines": {"obj": ListVaccine, "create": self.create_list_vaccine},
            "world_country_covid": {"obj": WorldStat, "create": self.create_world_country_covid},
            "ukraine_region_covid": {"obj": UkraineStat, "create": self.create_ukraine_region_covid},
            "ukraine_region_vaccine": {"obj": UkraineStatVaccine, "create": self.create_ukraine_region_vaccine} 
        }
        
    def _dataframe2object(self, tbl_name: str, data: pd.DataFrame) -> List[Any]:
        """Convert pandas dataframe to object for save.

        Args:
            tbl_name (str): sql table name;
            data (pd.DataFrame): dataframe with we want to convert;

        Returns:
            List[Any]: list of object
        """
        result = []
        for obj_parameters in data.to_dict(orient="records"):
            result.append(self.TABLE_LIST[tbl_name]["obj"](**obj_parameters))
        return result 

    def _save_data_to_database(self, tbl_name: str, data: pd.DataFrame) -> None:
        """Save data into sql table tbl_name
        1. convert pandas dataframe to object
        2. save object into DB;
        
        Args:
            tbl_name (str): sql table name;
            data (pd.DataFrame): data which we want save into sql DB/ 
        """
        object_list = self._dataframe2object(tbl_name=tbl_name, data=data)   # convert pandas dataframe to list of table object
        self.session.add_all(object_list)
        self.session.commit()
        self.session.close()

    def __create_covid_database(self) -> None:
        # if sqlite database is not exists -> create database and empty tables, else -> drop all table and create empty
        if not os.path.exists(Config.DATABASE_COVID_NAME):
            create_database()
            add_operations(self.session)
            add_sql_log(self.session, DBLogger(None, 4, datetime.datetime.now()))
            
    def refresh_sql_tables(self) -> None:
        """Refresh sql base:
        1. create sqlite database if doesn't exists
        2. create empty table and add data
        3. drop table (if exists), create empty, add new data
        """
   
        self.__create_covid_database()
          
        # get and inspect (for check tables exists) session engine and 
        engine = self.session.get_bind()
        engine_inspect = sa.inspect(engine)    
        
        for tbl_name, tbl_obj in self.TABLE_LIST.items():
            
            table_object = tbl_obj["obj"].__table__
            
            if engine_inspect.has_table(tbl_name):
                # ! delete table
                table_object.drop(engine)   
                # logs console/sql
                logger.opt(ansi=True).debug(f"SQL Table <green>{tbl_name}</green> : <green>DELETED</green> table")
                add_sql_log(self.session, DBLogger(tbl_name, 1, datetime.datetime.now()))
            
            # ! create empty table
            Base.metadata.create_all(engine, tables=[table_object])   
            # logs console/sql
            logger.opt(ansi=True).debug(f"SQL Table <green>{tbl_name}</green> : <green>CREATED</green> empty table")               
            add_sql_log(self.session, DBLogger(tbl_name, 2, datetime.datetime.now()))
            
            # create pandas dataframe and save into sql table
            dataframe_created = tbl_obj["create"]()
            self._save_data_to_database(tbl_name=tbl_name, data=dataframe_created)
            
            logger.opt(ansi=True).debug(f"SQL Table <green>{tbl_name}</green> : <green>INSERT</green> new data in empty table, #rows, #cols-{dataframe_created.shape}")
            add_sql_log(self.session, DBLogger(tbl_name, 3, datetime.datetime.now()))

         
        self.session.close()                   
