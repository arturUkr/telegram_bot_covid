import asyncio
import aioschedule
from schedulers.db_scheduler import schedule_refresh_covid_db
from schedulers.message_scheduler import schedule_send_message_country, schedule_send_message_ukraine
from utils.config import Config

# ! Sheduler MAIN ! #
async def scheduler():
    aioschedule.every().day.at(Config.DATABASE_COVID_REFRESH_TIME).do(schedule_refresh_covid_db)
    aioschedule.every().day.at(Config.SEND_COVID_MESSAGE_TIME).do(schedule_send_message_country)
    aioschedule.every().day.at(Config.SEND_COVID_MESSAGE_TIME).do(schedule_send_message_ukraine)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
