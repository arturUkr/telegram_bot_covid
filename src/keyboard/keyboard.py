from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import emoji


"""
1. World (button)
    1.1. world_top_country (inline)
        1.1.1. world_top_country_confirmed;
        1.1.2. world_top_country_deaths;
        1.1.3. world_top_country_existing;
    1.2. world_plot_country (inline)
        1.2.1. world_plot_country_confirmed;
        1.2.2. world_plot_country_deaths;
        1.2.3. world_plot_country_existing;

    
"""

# ! START keyboard -> Buttons (1, 2)
btn_world = KeyboardButton(text="/World")
btn_ukraine = KeyboardButton(text="/Ukraine")

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

keyboard.row(btn_world, 
             btn_ukraine)


# keyboard -> inlines (1.1, 1.2)

keyboard_inline_world = InlineKeyboardMarkup(row_width=1)

btn_inline_world_top = InlineKeyboardButton(text=f"{emoji.emojize(':world_map:')} Топ країн", 
                                            callback_data="world_top_country")
btn_inline_world_plot = InlineKeyboardButton(text=f"{emoji.emojize(':chart_increasing:')} Світова динаміка", 
                                             callback_data="world_plot_country")

keyboard_inline_world.row(btn_inline_world_top,
                          btn_inline_world_plot)
# ------

# (1.1.1, 1.1.2, 1.1.3)
keyboard_inline_world_variant = InlineKeyboardMarkup(row_width=1)

btn_inline_world_top_confirmed = InlineKeyboardButton(text=f"{emoji.emojize(':syringe:')} Нові випадки", 
                                                      callback_data="world_top_country_confirmed")
btn_inline_world_top_deaths = InlineKeyboardButton(text=f"{emoji.emojize(':red_square:')} Смерті", 
                                                   callback_data="world_top_country_deaths")
btn_inline_world_top_existing = InlineKeyboardButton(text=f"{emoji.emojize(':pill:')} Хворіє", 
                                                     callback_data="world_top_country_existing")

keyboard_inline_world_variant.row(btn_inline_world_top_confirmed,
                                  btn_inline_world_top_deaths,
                                  btn_inline_world_top_existing)

# (1.2.1, 1.2.2, 1.2.3)
keyboard_inline_world_plot_variant = InlineKeyboardMarkup(row_width=1)

btn_inline_world_plot_confirmed = InlineKeyboardButton(text=f"{emoji.emojize(':syringe:')} Нові випадки",
                                                       callback_data="world_plot_country_confirmed")
btn_inline_world_plot_deaths = InlineKeyboardButton(text=f"{emoji.emojize(':red_square:')} Смерті",
                                                    callback_data="world_plot_country_deaths")
btn_inline_world_plot_existing = InlineKeyboardButton(text=f"{emoji.emojize(':pill:')} Хворіє", 
                                                      callback_data="world_plot_country_existing")

keyboard_inline_world_plot_variant.row(btn_inline_world_plot_confirmed,
                                       btn_inline_world_plot_deaths,
                                       btn_inline_world_plot_existing)

