from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


gift_menu = InlineKeyboardMarkup(row_width=2)
gift_one_day = InlineKeyboardButton(text='Один день', callback_data='gift_one_day')
gift_three_day = InlineKeyboardButton(text='Три дня', callback_data='gift_three_day')
no_gift = InlineKeyboardButton(text='Без подарка', callback_data='gift_nogift')
gift_menu.add(gift_one_day).insert(gift_three_day).insert(no_gift)
