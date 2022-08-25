from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

referral_menu = InlineKeyboardMarkup(row_width=1)
statistic_referral_button = InlineKeyboardButton('Статистика📈', callback_data='statistic_referral')
referral_menu.insert(statistic_referral_button)
