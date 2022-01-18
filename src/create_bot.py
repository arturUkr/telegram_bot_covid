from aiogram import types, Bot, Dispatcher
from utils.utils import get_environment_variable
from covid import CovidSQLGetter, TelegramMessageCovidText, CovidPlotter
from db_models.database import Session


TELEGRAM_TOKEN = get_environment_variable("TELEGRAM_BOT_TOKEN")


bot = Bot(token=TELEGRAM_TOKEN)
bot_dispatcher = Dispatcher(bot=bot)


getter_obj = CovidSQLGetter(session=Session())
message_obj = TelegramMessageCovidText(getter_obj)
plotter_obj = CovidPlotter(getter_obj)
