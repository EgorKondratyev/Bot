from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_buy_vip_paypal_keyboard(one_day_price: int, three_day_price: int, week_day_price: int,
                                   month_day_price: int) -> InlineKeyboardMarkup:
    buy_vip_menu = InlineKeyboardMarkup(row_width=1)
    one_day = InlineKeyboardButton(text=f'1 День - {one_day_price}р', callback_data='vip_paypal_one_day')
    three_day = InlineKeyboardButton(text=f'3 Дня - {three_day_price}р', callback_data='vip_paypal_three_day')
    week = InlineKeyboardButton(text=f'🥰Неделя - {week_day_price}р🥰', callback_data='vip_paypal_week_day')
    month = InlineKeyboardButton(text=f'😍Месяц - {month_day_price}р😍', callback_data='vip_paypal_month_day')
    buy_vip_menu.add(one_day).add(three_day).add(week).add(month)
    return buy_vip_menu


def create_payment_vip_paypal_keyboard(url: str, payment_id: str, days: int) -> InlineKeyboardMarkup:
    payment_menu = InlineKeyboardMarkup(row_width=2)
    payment_url = InlineKeyboardButton(text='Оплатить💵', url=url)
    check_payment = InlineKeyboardButton(text='Проверить✅', callback_data=f'check_payment_{payment_id}_{days}')
    payment_menu.insert(payment_url).insert(check_payment)
    return payment_menu


def create_buy_king_chat_paypal_keyboard() -> InlineKeyboardMarkup:
    payment_menu = InlineKeyboardMarkup(row_width=1)
    payment_button = InlineKeyboardButton(text='👸Стать одним из королей чата🤴', callback_data='king_chat_buy')
    payment_menu.add(payment_button)
    return payment_menu


def create_payment_king_chat_paypal_keyboard(url: str, payment_id: str) -> InlineKeyboardMarkup:
    payment_menu = InlineKeyboardMarkup(row_width=2)
    payment_url = InlineKeyboardButton(text='Стать королем💵', url=url)
    check_payment = InlineKeyboardButton(text='Проверить оплату✅', callback_data=f'check_king_pay_{payment_id}')
    payment_menu.insert(payment_url).insert(check_payment)
    return payment_menu

