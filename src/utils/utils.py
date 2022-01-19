from aiogram import types
from typing import Union
import datetime
from utils.config import Config
from loguru import logger


def refresh_time_checker(func):
    
    async def wrapper(params: Union[types.Message, types.CallbackQuery]):
        
        user_ = params.from_user.id if isinstance(params, types.Message) else params.message.chat.id
            
        time_now = datetime.datetime.now()
        time_refresh_db = datetime.datetime.strptime(Config.DATABASE_COVID_REFRESH_TIME, "%H:%M").time()
        time_send_mess = datetime.datetime.strptime(Config.SEND_COVID_MESSAGE_TIME, "%H:%M").time()
        
        p1 = datetime.datetime(time_now.year, time_now.month, time_now.day, 
                               time_refresh_db.hour, time_refresh_db.minute, time_refresh_db.second)
        p2 = datetime.datetime(time_now.year, time_now.month, time_now.day, 
                               time_send_mess.hour, time_send_mess.minute, time_send_mess.second)  
        
        if p1 <= time_now < p2:
            text_ = "Вибачте, але зараз оновлюється база даних, отримати дані можна буде через декілька хвилин"
            if isinstance(params, types.Message):
                await params.answer(text=text_)
            else:
                await params.message.answer(text=text_)
            logger.debug(f"User {user_} send message when database refresh")
        else:
            return await func(params)

    return wrapper

'''
def auth(func):
    async def wrapper(message: types.Message):
        user_id = str(message.from_user.id)
        logger.debug(f'User {user_id} send message')
        if not bool(int(get_environment_variable("IS_BOT_PRODUCTION"))):
            if user_id != get_environment_variable("TELEGRAM_ADMIN_USER_ID"):
                return await message.reply("Access denied", reply=False)
        return await func(message)
    
    return wrapper
'''