from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from create_bot.bot import bot
from create_bot.admin_bot import admin_dp
from create_bot.config import admins
from databases.admin_side import BanUsersDB, ComplainsDB
from states.admin_states.ban_user_states import BanUserFSM, UnBanUserFSM


# @admin_dp.message_handler(commands='ban_user')
async def get_id_for_ban(message: Message):
    if message.chat.type == 'private' and message.from_user.id in admins:
        await message.answer('Вы зашли меню для блокировки пользователя\n\n'
                             'Теперь отправьте мне ID данного пользователя (для получения ID использовать бота '
                             'https://t.me/getmyid_bot\n\n'
                             'ID:')
        await BanUserFSM.get_id_user.set()


# @admin_dp.message_handler(state=BanUserFSM.get_id_user)
async def confirm(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('OK')
    if message.text.isdigit():
        try:
            user_ = await bot.get_chat(message.text)
            if user_:
                print(user_)
                async with state.proxy() as data:
                    data['user_id'] = message.text
                await message.answer(f'Вы хотите забанить следующего пользователя: \n'
                                     f'ID: {user_.id}\n'
                                     f'Не числовой ID: {user_.username}\n'
                                     f'Никнейм в телеграм: {user_.first_name}')
                await message.answer('Для подтверждения напишите "да"\n'
                                     'Для остановки напишите "stop"')
                await BanUserFSM.confirm.set()
            else:
                await message.answer('Данный пользователь никогда не пользовался ботом')
        except Exception:
            await message.answer('Данный пользователь никогда не пользовался ботом')
    else:
        await message.answer('ID может иметь только целочисленное значение')


# @admin_dp.message_handler(state=BanUserFSM.confirm)
async def ban_user(message: Message, state: FSMContext):
    if message.text.lower().strip() == 'да':
        async with state.proxy() as data:
            user_id = data['user_id']
        await state.finish()
        ban_db = BanUsersDB()
        if not ban_db.exists_user(user_id=user_id):
            ban_db.user_add(user_id=user_id)
            complain_db = ComplainsDB()
            complain_db.set_complain(user_id=user_id, amount_complains=0)
            await message.answer('Пользователь успешно забанен')
        else:
            await message.answer('Данный пользователь уже находится в бане')

    elif message.text.lower().strip() == 'stop':
        await state.finish()
        await message.answer('OK')

    else:
        await message.answer('Введите "да" или "stop" для продолжения')


# @admin_dp.message_handler(commands='unban_user')
async def get_id_for_unban(message: Message):
    if message.chat.type == 'private' and message.from_user.id in admins:
        await message.answer('Вы зашли меню для разблокировки пользователя\n\n'
                             'Теперь отправьте мне ID данного пользователя (для получения ID использовать бота '
                             'https://t.me/getmyid_bot\n\n'
                             'ID:')
        await UnBanUserFSM.get_id_user.set()


# @admin_dp.message_handler(state=UnBanUserFSM.get_id_user)
async def confirm_unban(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('OK')
    if message.text.isdigit():
        try:
            user_ = await bot.get_chat(message.text)
            if user_:
                print(user_)
                async with state.proxy() as data:
                    data['user_id'] = message.text
                await message.answer(f'Вы хотите разбанить следующего пользователя: \n'
                                     f'ID: {user_.id}\n'
                                     f'Не числовой ID: {user_.username}\n'
                                     f'Никнейм в телеграм: {user_.first_name}')
                await message.answer('Для подтверждения напишите "да"\n'
                                     'Для остановки напишите "stop"')
                await UnBanUserFSM.confirm.set()
            else:
                await message.answer('Данный пользователь никогда не пользовался ботом')
        except Exception:
            await message.answer('Данный пользователь никогда не пользовался ботом')
    else:
        await message.answer('ID может иметь только целочисленное значение')


# @admin_dp.message_handler(state=UnBanUserFSM.confirm)
async def unban_user(message: Message, state: FSMContext):
    if message.text.lower().strip() == 'да':
        async with state.proxy() as data:
            user_id = data['user_id']
        await state.finish()
        ban_db = BanUsersDB()
        if ban_db.exists_user(user_id=user_id):
            ban_db.delete_user(user_id=user_id)
            await message.answer('Пользователь успешно разбанен')
        else:
            await message.answer('Данный пользователь не забанен')

    elif message.text.lower().strip() == 'stop':
        await state.finish()
        await message.answer('OK')

    else:
        await message.answer('Введите "да" или "stop" для продолжения')


def register_handlers_ban_users():
    admin_dp.register_message_handler(get_id_for_ban, commands='ban_user')
    admin_dp.register_message_handler(confirm, state=BanUserFSM.get_id_user)
    admin_dp.register_message_handler(ban_user, state=BanUserFSM.confirm)
    admin_dp.register_message_handler(get_id_for_unban, commands='unban_user')
    admin_dp.register_message_handler(confirm_unban, state=UnBanUserFSM.get_id_user)
    admin_dp.register_message_handler(unban_user, state=UnBanUserFSM.confirm)
