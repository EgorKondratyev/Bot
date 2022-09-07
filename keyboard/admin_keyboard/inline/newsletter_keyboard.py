from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

menu_confrim = InlineKeyboardMarkup(row_width=1)
confrim_button = InlineKeyboardButton(text='✅Подтвердить✅', callback_data='go_newsletter')
cancel_button = InlineKeyboardButton(text='Отмена', callback_data='go_newsletter_stop')
menu_confrim.add(confrim_button).add(cancel_button)
