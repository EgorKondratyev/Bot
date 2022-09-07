from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import ChatNotFound

from create_bot.bot import bot
from create_bot.admin_bot import admin_dp
from create_bot.config import admins
from databases.payments import VIP
from keyboard.admin_keyboard.inline.issuance_vip_keyboard import vip_menu
from states.admin_states.issuance_vip_states import IssuanceVIPFSM


# @admin_dp.message_handler(commands='issuance_vip', state=None)
async def get_user_id(message: Message):
    if message.from_user.id in admins:
        await IssuanceVIPFSM.get_id.set()
        await message.answer('Вы зашли в меню выдачи VIP статуса для пользователя\n\n'
                             'Как получить ID? Можно воспользоваться функциями бесплатного бота в телеграм'
                             ' "https://t.me/getmyid_bot", который выдаст ID пользователя, который вам необходим.\n'
                             'Чтобы получить ID пользователя необходимо переслать любое сообщение пользователя '
                             'данному боту и бот выдаст его ID:\n\n'
                             'Отправьте мне его ID: \n')
        await message.answer('Для остановки напишите "stop"')


# @admin_dp.message_handler(state=IssuanceVIPFSM.get_id)
async def get_day_time(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('ОК')
        return

    if message.text.isdigit():
        try:
            user = await bot.get_chat(message.text)
            if user:
                await message.answer(f'Выдача VIP пользователю:\n\n'
                                     f'Имя: {user.first_name}\n'
                                     f'ID: {user.username}\n'
                                     f'Числовой ID: {user.id}\n\n'
                                     f'Если Вы уверены, что данному человеку необходимо выдать статус VIP, то '
                                     f'выберите один из ниже предложенных вариантов: ', reply_markup=vip_menu)
                async with state.proxy() as data:
                    data['user_id'] = user.id
                await IssuanceVIPFSM.day_time.set()
        except ChatNotFound:
            await message.answer(f'Прежде чем выдавать VIP стоит удостовериться, что человеком хотя бы раз '
                                 f'пользовался данным ботом\n\n'
                                 f'На данный момент человек с ID: {message.text} ни разу не пользовался ботом')
    else:
        await message.answer('ID может быть только числового формата!')


# @admin_dp.callback_query_handler(Text(startswith='issuance_vip_'), state=IssuanceVIPFSM.day_time)
async def issuance_vip(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'issuance_vip_stop':
        await callback.answer('OK')
        await state.finish()
        return
    await callback.answer('Начинаю выдачу VIP...')
    time_day = callback.data[len('issuance_vip_'):]
    async with state.proxy() as data:
        user_id = data['user_id']

    await state.finish()
    vip_db = VIP()
    text_vip = ''
    match time_day:
        case 'one':
            vip_db.update_status_vip(user_id=user_id, status_vip=True, time_vip=86400)
            text_vip += '1 день'
        case 'three':
            vip_db.update_status_vip(user_id=user_id, status_vip=True, time_vip=259200)
            text_vip += '3 дня'
        case 'week':
            vip_db.update_status_vip(user_id=user_id, status_vip=True, time_vip=604800)
            text_vip += 'Неделю'
        case 'month':
            vip_db.update_status_vip(user_id=user_id, status_vip=True, time_vip=2592000)
            text_vip += 'Месяц'

    await bot.send_message(chat_id=user_id, text=f'Вам был выдан VIP на {text_vip}')
    await callback.message.answer(f'VIP успешно выдан пользователю {user_id} на {text_vip}')


def register_handlers_issuance_vip():
    admin_dp.register_message_handler(get_user_id, commands='issuance_vip', state=None)
    admin_dp.register_message_handler(get_day_time, state=IssuanceVIPFSM.get_id)
    admin_dp.register_callback_query_handler(issuance_vip,
                                             Text(startswith='issuance_vip_'), state=IssuanceVIPFSM.day_time)

