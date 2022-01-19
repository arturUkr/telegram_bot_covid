from aiogram import types, Dispatcher
from aiogram.utils import emoji
from aiogram.dispatcher.filters import Text
import aiogram.utils.markdown as md
from create_bot import bot, message_obj, plotter_obj
from loguru import logger
from keyboard import keyboard_inline_world, keyboard_inline_world_variant, keyboard_inline_world_plot_variant
from utils.utils import refresh_time_checker


# Keyboard Button (World) -> Send Inline button (top country table, world dynamic plot)    
@refresh_time_checker
async def message_command_world(message: types.Message):
    """
        Call Inline Keyboard:
        1. Топ країн (callback_data=world_top_country) - топ 20 країн по кількості нових випадків коронавірусу, смертей, кількості тих, хто хворіє на останню доступну дату.  
        2. Світова динаміка (callback_data=world_total_plot) - графік щоденних нових випадків коронавірусу в світі.

        Args:
        message (types.Message): user message
    """

    user_ = message.from_user.id
    text_ = \
        md.text(
            f"{emoji.emojize(':small_orange_diamond:')}", 
            md.bold("Топ країн"), " - топ 20 країн по кількості нових випадків коронавірусу, смертей, кількості тих, хто хворіє на останню доступну дату. \n\n",
            f"{emoji.emojize(':small_orange_diamond:')}",
            md.bold("Світова динаміка"), " - графік щоденних даних коронавірусу в світі.",
            sep=""
        )
    logger.opt(ansi=True).debug(f"User {user_} click on Keyboard Button <green>world</green>")
   
    await bot.send_message(chat_id=user_, 
                           text=text_, 
                           reply_markup=keyboard_inline_world,
                           parse_mode=types.ParseMode.MARKDOWN)
    
    logger.opt(ansi=True).debug(f"Send Inline Keyboard <green>world_top_country</green>, <green>world_total_plot</green>")
    
 
 # Keyboard Button (World) -> Inline button (top country)-> Send Inline Button (deaths | confirmed | existing)
@refresh_time_checker
async def world_top_country_callback(callback: types.CallbackQuery):
    
    text_ = md.text(md.bold("Виберіть, по якому показнику показати топ країн:"))
    user_ = callback.message.chat.id    
    
    logger.opt(ansi=True).debug(f"User {user_} click on Inline Button <green>world_top_country</green>")
    
    await bot.send_message(chat_id=user_,
                           text=text_, 
                           reply_markup=keyboard_inline_world_variant,
                           parse_mode=types.ParseMode.MARKDOWN)
    await callback.answer()
    
    
# Keyboard Button (World) -> Inline button (top country)-> Send Inline Button (deaths | confirmed | existing) -> Send top country table
@refresh_time_checker
async def world_top_country_variant_callback(callback: types.CallbackQuery):
    
    config_ = {
        "world_top_country_confirmed": "confirmed",
        "world_top_country_deaths": "deaths",
        "world_top_country_existing": "existing"
    }

    user_ = callback.message.chat.id
    button_ = config_.get(callback.data)
    text_ = message_obj.get_message_top_country_for_last_date(top_n=20, data_name=button_)

    logger.opt(ansi=True).debug(f"User {user_} click on Inline Button <green> {button_} </green>")

    await bot.send_message(chat_id=user_,
                           text=text_, 
                           parse_mode=types.ParseMode.MARKDOWN,
                           reply_markup=keyboard_inline_world_variant)
    await callback.answer()
    

# Keyboard Button (World) -> Inline button (dynamic plot)-> Send Inline Button (deaths | confirmed | existing)
@refresh_time_checker
async def world_plot_country_callback(callback: types.CallbackQuery):
   
    user_ = callback.message.chat.id
    text_ = md.text(md.bold("Виберіть, по якому показнику показати світову динаміку:"))

    logger.opt(ansi=True).debug(f"User {user_} click on Inline Button <green>world_plot_country</green>")
    
    await bot.send_message(chat_id=user_, 
                           text=text_, 
                           reply_markup=keyboard_inline_world_plot_variant,
                           parse_mode=types.ParseMode.MARKDOWN)
    await callback.answer()
    
    
# Keyboard Button (World) -> Inline button (dynamic plot)-> Inline Button (deaths | confirmed | existing) -> Send world dynamic plot (lineplot)
@refresh_time_checker
async def world_plot_country_variant_callback(callback: types.CallbackQuery):
    
    config_ = {
        "world_plot_country_confirmed": "confirmed",
        "world_plot_country_deaths": "deaths",
        "world_plot_country_existing": "existing"
    }
    user_ = callback.message.chat.id
    button_ = config_.get(callback.data)
    photo_ = plotter_obj.create_world_dynamics_plot(data_name=button_)
    logger.opt(ansi=True).debug(f"User {user_} click on Inline Button <green>{button_.upper()}</green>")
    
    await bot.send_photo(chat_id=user_,
                         photo=photo_,
                         reply_markup=keyboard_inline_world_plot_variant, 
                         parse_mode=types.ParseMode.MARKDOWN)
    await callback.answer()
    
        
def register_handlers_world(dp: Dispatcher):
    
    dp.register_message_handler(message_command_world, commands=["world"])
    dp.register_callback_query_handler(world_top_country_callback, text="world_top_country")
    dp.register_callback_query_handler(world_top_country_variant_callback, Text(startswith="world_top_country_"))
    dp.register_callback_query_handler(world_plot_country_callback, text="world_plot_country")
    dp.register_callback_query_handler(world_plot_country_variant_callback, Text(startswith="world_plot_country_"))
