from aiogram import Bot, Dispatcher
from covid import CovidSQLGetter, TelegramMessageCovidText, CovidPlotter
from db_models.database import Session
from utils.config import Config


bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
bot_dispatcher = Dispatcher(bot=bot)


getter_obj = CovidSQLGetter(session=Session())
message_obj = TelegramMessageCovidText(getter_obj)
plotter_obj = CovidPlotter(getter_obj)
