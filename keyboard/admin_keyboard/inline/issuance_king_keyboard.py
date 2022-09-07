from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


king_menu = InlineKeyboardMarkup(row_width=1)
confirm_button = InlineKeyboardButton(text='✅Подтвердить✅', callback_data='king_menu_confirm')
cancel_button = InlineKeyboardButton(text='Отмена', callback_data='king_menu_cancel')
king_menu.add(confirm_button).add(cancel_button)
