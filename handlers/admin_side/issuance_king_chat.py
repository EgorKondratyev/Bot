from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import ChatNotFound

from create_bot.bot import bot
from create_bot.admin_bot import admin_dp
from create_bot.config import admins
from databases.payments import KingChatDB
from keyboard.admin_keyboard.inline.issuance_king_keyboard import king_menu
from states.admin_states.issuance_king_states import IssuanceKingFSM


# @admin_dp.message_handler(commands='issuance_king', state=None)
async def get_user_id(message: Message):
    if message.from_user.id in admins:
        await IssuanceKingFSM.get_id.set()
        await message.answer('Вы зашли в меню выдачи статуса короля для пользователя\n\n'
                             'Как получить ID? Можно воспользоваться функциями бесплатного бота в телеграм'
                             ' "https://t.me/getmyid_bot", который выдаст ID пользователя, который вам необходим.\n'
                             'Чтобы получить ID пользователя необходимо переслать любое сообщение пользователя '
                             'данному боту и бот выдаст его ID:\n\n'
                             'Отправьте мне его ID: \n')
        await message.answer('Для остановки напишите "stop"')


# @admin_dp.message_handler(state=IssuanceKingFSM.get_id)
async def confirm(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('ОК')
        return

    if message.text.isdigit():
        try:
            user = await bot.get_chat(message.text)
            if user:
                await message.answer(f'Выдача статуса короля пользователю:\n\n'
                                     f'Имя: {user.first_name}\n'
                                     f'ID: {user.username}\n'
                                     f'Числовой ID: {user.id}\n\n'
                                     f'Если Вы уверены, что хотите выдать статус короля данному человеку, то '
                                     f'подтвердите свое действие по кнопке ниже', reply_markup=king_menu)
                async with state.proxy() as data:
                    data['user_id'] = user.id
                await IssuanceKingFSM.confirm.set()
        except ChatNotFound:
            await message.answer(f'Прежде чем выдавать статус короля стоит удостовериться, что человеком хотя бы раз '
                                 f'пользовался данным ботом\n\n'
                                 f'На данный момент человек с ID: {message.text} ни разу не пользовался ботом')
    else:
        await message.answer('ID может быть только числового формата!')


# @admin_dp.callback_query_handler(Text(startswith='king_menu_'), state=IssuanceKingFSM.confirm)
async def issuance_king_status(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'king_menu_cancel':
        await callback.answer('OK')
        await state.finish()
        return
    await callback.answer('Начинаю выдачу статуса короля...')
    async with state.proxy() as data:
        user_id = data['user_id']

    await state.finish()
    king_chat_db = KingChatDB()
    amount_users = len(king_chat_db.get_users_id())
    if amount_users < 3:
        king_chat_db.add_user(user_id=user_id)
    else:
        delete_user_id = king_chat_db.get_users_id()[0][0]
        king_chat_db.delete_user(delete_user_id)
        king_chat_db.add_user(user_id=user_id)

    await callback.message.answer(f'Статус короля успешно выдан пользователю {user_id}')
    await bot.send_message(chat_id=user_id, text='С этих пор Вы являетесь равноправным членом королевства!\n\n'
                                                 'Благодарим за приобретение одного из мест на королевском троне')


def register_handlers_issuance_king_status():
    admin_dp.register_message_handler(get_user_id, commands='issuance_king', state=None)
    admin_dp.register_message_handler(confirm, state=IssuanceKingFSM.get_id)
    admin_dp.register_callback_query_handler(issuance_king_status, Text(startswith='king_menu_'),
                                             state=IssuanceKingFSM.confirm)

