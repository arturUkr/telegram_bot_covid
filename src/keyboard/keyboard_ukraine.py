from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import flag
from aiogram.utils import emoji


"""
2. Ukraine (button) 
    2.1. Ukraine
        2.1.1. global info
        2.1.2. dynamic
            2.1.2.1. confirmed
            2.1.2.2. deaths
            2.1.2.3. vaccines
    2.2. Regions
        2.2.1. global info
        2.2.2. dynamic
"""

# Ukraine -> inline: Ukraine, Regions
keyboard_inline_ukraine = InlineKeyboardMarkup(row_width=2)
btn_inline_ukraine_global = InlineKeyboardButton(text=f"{emoji.emojize(flag.flag('UA'))} Україна", callback_data="ukraine_global")
btn_inline_ukraine_regions = InlineKeyboardButton(text="Регіони", callback_data="ukraine_regions")
keyboard_inline_ukraine.row(btn_inline_ukraine_global,
                            btn_inline_ukraine_regions)
