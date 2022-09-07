from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from databases.client_side import LanguageDB
from utilits.translate_text import translate_from_lang_russian


async def create_buy_vip_paypal_keyboard(one_day_price: int, three_day_price: int, week_day_price: int,
                                         month_day_price: int, user_id: int) -> InlineKeyboardMarkup:
    language_db = LanguageDB()
    if language_db.get_language_user(user_id=user_id) == 'en':
        one_day_text = '1 day'
        three_day_text = '3 days'
        week_day_text = 'A week'
        month_day_text = 'Month'
    else:
        one_day_text = await translate_from_lang_russian(user_id=user_id, text='1 День')
        three_day_text = await translate_from_lang_russian(user_id=user_id, text='3 Дня')
        week_day_text = await translate_from_lang_russian(user_id=user_id, text='Неделя')
        month_day_text = await translate_from_lang_russian(user_id=user_id, text='Месяц')
    buy_vip_menu = InlineKeyboardMarkup(row_width=1)
    one_day = InlineKeyboardButton(text=one_day_text + f' - {one_day_price}$', callback_data='vip_paypal_one_day')
    three_day = InlineKeyboardButton(text=three_day_text + f' - {three_day_price}$',
                                     callback_data='vip_paypal_three_day')
    week = InlineKeyboardButton(text=week_day_text + f' - {week_day_price}$🥰', callback_data='vip_paypal_week_day')
    month = InlineKeyboardButton(text=month_day_text + f' - {month_day_price}$😍', callback_data='vip_paypal_month_day')
    buy_vip_menu.add(one_day).add(three_day).add(week).add(month)
    return buy_vip_menu


async def create_payment_vip_paypal_keyboard(url: str, payment_id: str, days: int,
                                             user_id: int) -> InlineKeyboardMarkup:
    language_db = LanguageDB()
    if language_db.get_language_user(user_id=user_id) == 'en':
        payment_url_text = 'To pay'
        check_text = 'Check'
    else:
        payment_url_text = await translate_from_lang_russian(user_id=user_id, text='Оплатить')
        check_text = await translate_from_lang_russian(user_id=user_id, text='Проверить')
    payment_menu = InlineKeyboardMarkup(row_width=2)
    payment_url = InlineKeyboardButton(text=payment_url_text + '💵', url=url)
    check_payment = InlineKeyboardButton(text=check_text + '✅', callback_data=f'check_payment_{payment_id}_{days}')
    payment_menu.insert(payment_url).insert(check_payment)
    return payment_menu


async def create_buy_king_chat_paypal_keyboard(user_id: int) -> InlineKeyboardMarkup:
    king_chat_text = await translate_from_lang_russian(user_id=user_id,
                                                       text='Стать одним из королей чата')
    payment_menu = InlineKeyboardMarkup(row_width=1)
    payment_button = InlineKeyboardButton(text='👸' + king_chat_text + '🤴', callback_data='king_chat_buy')
    payment_menu.add(payment_button)
    return payment_menu


async def create_payment_king_chat_paypal_keyboard(url: str, payment_id: str, user_id: int) -> InlineKeyboardMarkup:
    king_chat_text = await translate_from_lang_russian(user_id=user_id, text='Стать королем')
    check_text = await translate_from_lang_russian(user_id=user_id, text='Проверить оплату')
    payment_menu = InlineKeyboardMarkup(row_width=2)
    payment_url = InlineKeyboardButton(text=king_chat_text + '💵', url=url)
    check_payment = InlineKeyboardButton(text=check_text + '✅', callback_data=f'check_king_pay_{payment_id}')
    payment_menu.insert(payment_url).insert(check_payment)
    return payment_menu
