from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

state_top_menu = InlineKeyboardMarkup(row_width=2)
top_button = InlineKeyboardButton(text='Включить топ🔝', callback_data='state_on_top')
king_button = InlineKeyboardButton(text='Включить королевство👑', callback_data='state_on_king')
state_top_menu.insert(top_button).insert(king_button)
