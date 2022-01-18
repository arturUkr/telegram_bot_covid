import asyncio
import aioschedule
from schedulers.db_scheduler import schedule_refresh_covid_db
from schedulers.message_scheduler import schedule_send_message_country, schedule_send_message_ukraine


# ! Sheduler MAIN ! #
async def scheduler():
    aioschedule.every().day.at("10:00").do(schedule_refresh_covid_db)
    aioschedule.every().day.at("10:10").do(schedule_send_message_country)
    aioschedule.every().day.at("10:10").do(schedule_send_message_ukraine)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
