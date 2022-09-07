from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from create_bot.admin_bot import admin_dp
from create_bot.config import admins
from databases.payments import PriceDB
from keyboard.admin_keyboard.inline.change_price_keyboard import change_price_menu
from states.admin_states.change_price_states import ChangePriceFSM
from log.log import logger


# @admin_dp.message_handler(commands='change_price')
async def choice_change_price(message: Message):
    if message.from_user.id in admins:
        await message.answer('Вы находитесь в меню для изменения цен\n\n'
                             'Выберите один из ниже интересующих Вас вариантов', reply_markup=change_price_menu)


# @admin_dp.callback_query_handler(Text(startswith='change_price_'), states=None)
async def get_price(callback: CallbackQuery):
    await callback.answer()
    product = callback.data[len('change_price_'):]
    match product:
        case 'one':
            await callback.message.answer('Вы выбрали изменение цены для VIP "один день"\n\n'
                                          'Для отмены напишите "stop"')
            await ChangePriceFSM.one_day.set()
        case 'three':
            await callback.message.answer('Вы выбрали изменение цены для VIP "три дня"\n\n'
                                          'Для отмены напишите "stop"')
            await ChangePriceFSM.three_day.set()
        case 'week':
            await callback.message.answer('Вы выбрали изменение цены для VIP "неделя"\n\n'
                                          'Для отмены напишите "stop"')
            await ChangePriceFSM.week_day.set()
        case 'month':
            await callback.message.answer('Вы выбрали изменение цены для VIP "месяц"\n\n'
                                          'Для отмены напишите "stop"')
            await ChangePriceFSM.month_day.set()
        case 'king':
            await callback.message.answer('Вы выбрали изменение цены для короля чата\n\n'
                                          'Для отмены напишите "stop"')
            await ChangePriceFSM.king_chat.set()
    await callback.message.answer('Напишите необходимую цену: ')


# @admin_dp.message_handler(state=ChangePriceFSM.one_day)
async def change_price_one_day(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('OK')
    if message.text.isdigit():
        price_db = PriceDB()
        price_db.update_one_day_price(price=int(message.text))
        await message.answer('Цена успешно обновлена!')
        await state.finish()
    else:
        await message.answer('Цена должна иметь числовой вид!')


# @admin_dp.message_handler(state=ChangePriceFSM.three_day)
async def change_price_three_day(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('OK')
    if message.text.isdigit():
        price_db = PriceDB()
        price_db.update_three_day_price(price=int(message.text))
        await message.answer('Цена успешно обновлена!')
        await state.finish()
    else:
        await message.answer('Цена должна иметь числовой вид!')


# @admin_dp.message_handler(state=ChangePriceFSM.week_day)
async def change_price_week_day(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('OK')
    if message.text.isdigit():
        price_db = PriceDB()
        price_db.update_week_day_price(price=int(message.text))
        await message.answer('Цена успешно обновлена!')
        await state.finish()
    else:
        await message.answer('Цена должна иметь числовой вид!')


# @admin_dp.message_handler(state=ChangePriceFSM.month_day)
async def change_price_month_day(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('OK')
    if message.text.isdigit():
        price_db = PriceDB()
        price_db.update_month_day_price(price=int(message.text))
        await message.answer('Цена успешно обновлена!')
        await state.finish()
    else:
        await message.answer('Цена должна иметь числовой вид!')


# @admin_dp.message_handler(state=ChangePriceFSM.king_chat)
async def change_price_king_chat(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('OK')
    if message.text.isdigit():
        price_db = PriceDB()
        price_db.update_king_chat_price(price=int(message.text))
        await message.answer('Цена успешно обновлена!')
        await state.finish()
    else:
        await message.answer('Цена должна иметь числовой вид!')


def register_handlers_change_price():
    admin_dp.register_message_handler(choice_change_price, commands='change_price')
    admin_dp.register_callback_query_handler(get_price, Text(startswith='change_price_'), states=None)
    admin_dp.register_message_handler(change_price_one_day, state=ChangePriceFSM.one_day)
    admin_dp.register_message_handler(change_price_three_day, state=ChangePriceFSM.three_day)
    admin_dp.register_message_handler(change_price_week_day, state=ChangePriceFSM.week_day)
    admin_dp.register_message_handler(change_price_month_day, state=ChangePriceFSM.month_day)
    admin_dp.register_message_handler(change_price_king_chat, state=ChangePriceFSM.king_chat)
