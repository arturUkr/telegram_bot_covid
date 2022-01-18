from aiogram import types
from create_bot import bot, message_obj


# ! Scheduler -> messages
async def schedule_send_message_country():
    
    await bot.send_message(chat_id=379346159, 
                           text=message_obj.get_message_top_country_for_last_date(), 
                           parse_mode=types.ParseMode.MARKDOWN)
    
    
async def schedule_send_message_ukraine():
    
    await bot.send_message(chat_id=379346159,
                           text=message_obj.get_message_ukraine_main(),
                           parse_mode=types.ParseMode.MARKDOWN)
