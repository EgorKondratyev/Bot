from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


change_price_menu = InlineKeyboardMarkup(row_width=2)
change_one_day_button = InlineKeyboardButton(text='Один день', callback_data='change_price_one')
change_three_day_button = InlineKeyboardButton(text='Три дня', callback_data='change_price_three')
change_week_button = InlineKeyboardButton(text='Неделя', callback_data='change_price_week')
change_month_button = InlineKeyboardButton(text='Месяц', callback_data='change_price_month')
change_king_chat_button = InlineKeyboardButton(text='Король чата', callback_data='change_price_king')
change_price_menu.insert(change_one_day_button).insert(change_three_day_button).insert(change_week_button)\
    .insert(change_month_button).add(change_king_chat_button)
