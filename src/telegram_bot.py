from aiogram import types, Bot, Dispatcher, executor
from aiogram.dispatcher.filters import Text
from aiogram.utils import emoji
import aiogram.utils.markdown as md
from aiogram.types import ParseMode

from utils.utils import get_environment_variable
from covid import CovidSQLSaver, CovidSQLGetter, TelegramMessageCovidText
from db_models.database import Session

from keyboard import keyboard, keyboard_inline_world, keyboard_inline_world_variant, keyboard_inline_world_plot_variant
from keyboard import keyboard_inline_ukraine

from schedulers.db_scheduler import schedule_refresh_covid_db
from covid.data_plotter import CovidPlotter

import asyncio
import aioschedule
from loguru import logger

import matplotlib
import matplotlib.pyplot as plt

# doesn't show plot on server
matplotlib.use("Agg")
plt.ioff()


# ! Bot initialize BOT & DISPETCHER
bot = Bot(token=get_environment_variable("TELEGRAM_BOT_TOKEN"))
bot_dispatcher = Dispatcher(bot=bot)

getter_obj = CovidSQLGetter(session=Session())
message_obj = TelegramMessageCovidText(getter_obj)
plotter_obj = CovidPlotter(getter_obj)

# ! Scheduler -> messages
async def schedule_send_message_country():
    await bot.send_message(chat_id=379346159, 
                           text=message_obj.get_message_top_country_for_last_date(), 
                           parse_mode=ParseMode.MARKDOWN)


async def schedule_send_message_ukraine():
    await bot.send_message(chat_id=379346159,
                           text=message_obj.get_message_ukraine_main(),
                           parse_mode=ParseMode.MARKDOWN)

# ! Sheduler MAIN ! #
async def scheduler():
    aioschedule.every().day.at("10:00").do(schedule_refresh_covid_db)
    aioschedule.every().day.at("10:10").do(schedule_send_message_country)
    aioschedule.every().day.at("10:10").do(schedule_send_message_ukraine)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

# --------------------------------------------------------------------------------------------------

# ! START PROCESS BEFORE RUN OTHER
async def on_startup(_):
    asyncio.create_task(scheduler())

# --------------------------------------------------------------------------------------------------


@bot_dispatcher.message_handler(commands="start")
async def start_message(message: types.Message):
    
    await bot.send_message(chat_id=message.chat.id, text="artur", reply_markup=keyboard) 
    logger.opt(ansi=True).debug(f"User send command <green>start</green>, activate keyboard buttons ..., ...")


# Keyboard Button (World) -> Send Inline button (top country table, world dynamic plot)    
@bot_dispatcher.message_handler(commands="world")
async def message_command_world(message: types.Message):
    """
        Call Inline Keyboard:
        1. Топ країн (callback_data=world_top_country) - топ 20 країн по кількості нових випадків коронавірусу, смертей, кількості тих, хто хворіє на останню доступну дату.  
        2. Світова динаміка (callback_data=world_total_plot) - графік щоденних нових випадків коронавірусу в світі.

        Args:
        message (types.Message): user message
    """
    text_ = \
        md.text(
            f"{emoji.emojize(':small_orange_diamond:')}", 
            md.bold("Топ країн"), " - топ 20 країн по кількості нових випадків коронавірусу, смертей, кількості тих, хто хворіє на останню доступну дату. \n\n",
            f"{emoji.emojize(':small_orange_diamond:')}",
            md.bold("Світова динаміка"), " - графік щоденних даних коронавірусу в світі.",
            sep=""
        )
    user_ = message.from_user.id
    logger.opt(ansi=True).debug(f"User {user_} click on Keyboard Button <green>world</green>")
    await bot.send_message(chat_id=user_, 
                           text=text_, 
                           reply_markup=keyboard_inline_world,
                           parse_mode=ParseMode.MARKDOWN)
    logger.opt(ansi=True).debug(f"Send Inline Keyboard <green>world_top_country</green>, <green>world_total_plot</green>")
    

# Keyboard Button (World) -> Inline button (top country)-> Send Inline Button (deaths | confirmed | existing)
@bot_dispatcher.callback_query_handler(text="world_top_country")
async def world_top_country_callback(callback: types.CallbackQuery):
    
    text_ = md.text(md.bold("Виберіть, по якому показнику показати топ країн:"))
    user_ = callback.message.chat.id    
    logger.opt(ansi=True).debug(f"User {user_} click on Inline Button <green>world_top_country</green>")
    
    await bot.send_message(chat_id=user_, text=text_, reply_markup=keyboard_inline_world_variant, parse_mode=types.ParseMode.MARKDOWN)
    await callback.answer()

# Keyboard Button (World) -> Inline button (top country)-> Send Inline Button (deaths | confirmed | existing) -> Send top country table
@bot_dispatcher.callback_query_handler(Text(startswith="world_top_country_"))    
async def world_top_country_variant_callback(callback: types.CallbackQuery):
    
    config_ = {
        "world_top_country_confirmed": "confirmed",
        "world_top_country_deaths": "deaths",
        "world_top_country_existing": "existing"
    }
    button_ = config_.get(callback.data)
    text_ = message_obj.get_message_top_country_for_last_date(top_n=20, data_name=button_)
    user_ = callback.message.chat.id
    logger.opt(ansi=True).debug(f"User {user_} click on Inline Button <green> {button_} </green>")

    await bot.send_message(chat_id=user_,
                           text=text_, 
                           parse_mode=types.ParseMode.MARKDOWN,
                           reply_markup=keyboard_inline_world_variant)
    await callback.answer()

# Keyboard Button (World) -> Inline button (dynamic plot)-> Send Inline Button (deaths | confirmed | existing)
@bot_dispatcher.callback_query_handler(text="world_plot_country")
async def world_plot_country_callback(callback: types.CallbackQuery):
   
    text_ = md.text(md.bold("Виберіть, по якому показнику показати світову динаміку:"))
    user_ = callback.message.chat.id
    logger.opt(ansi=True).debug(f"User {user_} click on Inline Button <green>world_plot_country</green>")
    
    await bot.send_message(chat_id=user_, text=text_, reply_markup=keyboard_inline_world_plot_variant, parse_mode=types.ParseMode.MARKDOWN)
    await callback.answer()


# Keyboard Button (World) -> Inline button (dynamic plot)-> Inline Button (deaths | confirmed | existing) -> Send world dynamic plot (lineplot)
@bot_dispatcher.callback_query_handler(Text(startswith="world_plot_country_"))
async def world_plot_country_variant_callback(callback: types.CallbackQuery):
    
    config_ = {
        "world_plot_country_confirmed": "confirmed",
        "world_plot_country_deaths": "deaths",
        "world_plot_country_existing": "existing"
    }
    button_ = config_.get(callback.data)
    photo_ = plotter_obj.create_world_dynamics_plot(data_name=button_)
    user_ = callback.message.chat.id
    logger.opt(ansi=True).debug(f"User {user_} click on Inline Button <green>{button_.upper()}</green>")
    
    await bot.send_photo(chat_id=user_, photo=photo_, reply_markup=keyboard_inline_world_plot_variant, parse_mode=ParseMode.MARKDOWN)
    await callback.answer()


# ! Ukraine

@bot_dispatcher.message_handler(commands=['Ukraine'])
async def message_command_ukraine(message: types.Message):
    text_ = "Ukraine"
    user_ = message.chat.id
    logger.debug(f"User {user_} click Keyboard Button Ukraine")
    
    await bot.send_message(chat_id=user_, text=text_, reply_markup=keyboard_inline_ukraine, parse_mode=ParseMode.MARKDOWN)
    

@bot_dispatcher.callback_query_handler(text="ukraine_global")
async def ukraine_global_ukraine(callback: types.CallbackQuery):
    
    user_ = callback.message.chat.id
    text_ = message_obj.get_message_ukraine_main(add_regions=False)
    logger.opt(ansi=True).debug(f"User {user_} click on inline button <green>Ukraine</green>")

    plot_group = []
    for plot_ in ["confirmed", "deaths", "recovered", "existing"]: # , "count_vaccine"
        plot_group.append(types.InputMediaPhoto(types.InputFile(plotter_obj.create_ukraine_dynamics_plot(data_name=plot_))))

    await bot.send_message(chat_id=user_, text=text_, parse_mode=ParseMode.MARKDOWN)    
    await bot.send_media_group(chat_id=user_, media=plot_group)    
    await callback.answer()

    

@bot_dispatcher.message_handler()
async def echo_bot(message: types.Message):
    
    await bot.send_message(chat_id=message.chat.id, 
                           text=message_obj.get_message_ukraine_main(),
                           parse_mode=types.ParseMode.MARKDOWN)


if __name__ == "__main__":
    
    #a = CovidSQLSaver(Session())
    #a.refresh_sql_tables()       

    # ! bot run
    executor.start_polling(dispatcher=bot_dispatcher, 
                           skip_updates=True, 
                           on_startup=on_startup)
    
        
    
    
    

    


    
    
    
