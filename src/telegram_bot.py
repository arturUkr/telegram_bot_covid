import asyncio
from aiogram import executor
from loguru import logger
from dotenv import load_dotenv
import os
import matplotlib
import matplotlib.pyplot as plt

from schedulers import scheduler
from create_bot import bot_dispatcher
from handler import register_handlers_world, register_handlers_ukraine, register_handlers_other
from utils.config import Config

# doesn't show plot on server
matplotlib.use("Agg")
plt.ioff()


# ! START PROCESS BEFORE RUN OTHER
async def on_startup(_):
    logger.debug("START COVID BOT")
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    
    # ! add message and callback handlers
    register_handlers_world(dp=bot_dispatcher)
    register_handlers_ukraine(dp=bot_dispatcher)
    register_handlers_other(dp=bot_dispatcher)
    
    #a = CovidSQLSaver(Session())
    #a.refresh_sql_tables()       
    
    # ! bot run
    executor.start_polling(dispatcher=bot_dispatcher, 
                           skip_updates=True, 
                           on_startup=on_startup)
