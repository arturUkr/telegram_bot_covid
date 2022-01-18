from aiogram import types, Dispatcher
from create_bot import bot, message_obj
from loguru import logger
from keyboard import keyboard


# @bot_dispatcher.message_handler(commands="start")
async def start_message(message: types.Message):
    
    await bot.send_message(chat_id=message.chat.id, text="artur", reply_markup=keyboard) 
    logger.opt(ansi=True).debug(f"User send command <green>start</green>, activate keyboard buttons ..., ...")


#@bot_dispatcher.message_handler()
async def echo_bot(message: types.Message):
    
    await bot.send_message(chat_id=message.chat.id, 
                           text=message_obj.get_message_ukraine_main(),
                           parse_mode=types.ParseMode.MARKDOWN)
    
    
def register_handlers_other(dp: Dispatcher):
    
    dp.register_message_handler(start_message, commands=["start"])
    dp.register_message_handler(echo_bot)
    