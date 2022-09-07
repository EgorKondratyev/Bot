from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


vip_menu = InlineKeyboardMarkup(row_width=2)
one_day = InlineKeyboardButton(text='1 день', callback_data='issuance_vip_one')
three_day = InlineKeyboardButton(text='3 дня', callback_data='issuance_vip_three')
week = InlineKeyboardButton(text='Неделя', callback_data='issuance_vip_week')
month = InlineKeyboardButton(text='Месяц', callback_data='issuance_vip_month')
cancel_button = InlineKeyboardButton(text='Отмена', callback_data='issuance_vip_stop')
vip_menu.insert(one_day).insert(three_day).insert(week).insert(month).add(cancel_button)
