from aiogram import types, Dispatcher
from create_bot import bot, message_obj, plotter_obj
from loguru import logger
from keyboard import keyboard_inline_ukraine
from utils.utils import refresh_time_checker


@refresh_time_checker
async def message_command_ukraine(message: types.Message):
    
    user_ = message.chat.id
    text_ = "Ukraine"
    
    logger.debug(f"User {user_} click Keyboard Button Ukraine")
    
    await bot.send_message(chat_id=user_, 
                           text=text_, 
                           reply_markup=keyboard_inline_ukraine, 
                           parse_mode=types.ParseMode.MARKDOWN)


@refresh_time_checker
async def ukraine_global_ukraine(callback: types.CallbackQuery):
    
    user_ = callback.message.chat.id
    text_ = message_obj.get_message_ukraine_main(add_regions=False)
    
    logger.opt(ansi=True).debug(f"User {user_} click on inline button <green>Ukraine</green>")

    plot_group = []
    for plot_ in ["confirmed", "deaths", "recovered", "existing"]: # , "count_vaccine"
        plot_group.append(types.InputMediaPhoto(types.InputFile(plotter_obj.create_ukraine_dynamics_plot(data_name=plot_))))

    await bot.send_message(chat_id=user_, 
                           text=text_, 
                           parse_mode=types.ParseMode.MARKDOWN)  
      
    await bot.send_media_group(chat_id=user_,
                               media=plot_group)    
    await callback.answer()
    
    
def register_handlers_ukraine(dp: Dispatcher) -> None:
    
    dp.register_message_handler(message_command_ukraine, commands=['Ukraine'])
    dp.register_callback_query_handler(ukraine_global_ukraine, text="ukraine_global")
