from distutils.log import debug
from db_models.database import Session
from covid import CovidSQLSaver
from loguru import logger


async def schedule_refresh_covid_db():
    refresh_obj = CovidSQLSaver(session=Session(), country="all", regions="all")
    refresh_obj.refresh_sql_tables()
    logger.debug("Database covid refresh")
