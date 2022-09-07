from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from create_bot.admin_bot import admin_dp
from create_bot.config import admins
from databases.admin_side import ChannelDB
from states.admin_states.sub_channel_states import SubChannelFSM


# @admin_dp.message_handler(commands='add_sub_channel', state=None)
async def get_channel_id(message: Message):
    if message.from_user.id in admins:
        await message.answer('Вы зашли в меню добавления нового канала для пользования ботом!\n\n'
                             'Важное замечание, чтобы бот мог проверять подписку на канал бот должен состоять в данном '
                             'канале и иметь статус "Админа". В противном случае бот может зависнуть или не давать '
                             'воспользоваться пользователям данным ботом\n\n'
                             'Введите ID (примеры ID: (@physics_lib) канала: ')
        await SubChannelFSM.get_channel_id.set()
        await message.answer('Для отмены напишите "stop"')


# @admin_dp.message_handler(state=SubChannelFSM.get_channel_id)
async def get_channel_name(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('OK')
        return
    async with state.proxy() as data:
        data['channel_id'] = message.text
    await message.answer('Отлично. Теперь отправь мне имя, которое будет находиться в кнопке при переходе '
                         'на этот канал (имя может быть абсолютно любое): ')
    await message.answer('Для отмены напишите "stop"')
    await SubChannelFSM.get_channel_name.set()


# @admin_dp.message_handler(state=SubChannelFSM)
async def set_sub_channel(message: Message, state: FSMContext):
    async with state.proxy() as data:
        channel_id = data['channel_id']
    channel_name = message.text
    await state.finish()
    channel_db = ChannelDB()
    if not channel_db.exists_channel(channel_id=channel_id):
        channel_db.add_channel(channel_id=channel_id, channel_name=channel_name)
        await message.answer('Канал успешно добавлен в бота!')
    else:
        await message.answer('Данный канал уже есть в боте!')


# @admin_dp.register_message_handler(commands='delete_channel')
async def delete_channel(message: Message):
    if message.from_user.id in admins:
        channel_id = message.text[len('/delete_channel '):]
        channel_db = ChannelDB()
        if not channel_id:
            channels = channel_db.get_channels()
            text_channel = 'Чтобы удалить канал необходимо ввести команду "/delete_channel channel_id".\n\n' \
                           'Пример: /delete_channel @physics_lib\n\n' \
                           'Все имеющиеся в боте channel_id:\n\n'
            for i, channel in enumerate(channels, 1):
                text_channel += f'{i}. {channel[0]}\n'
            await message.answer(text_channel)
        else:
            if channel_db.exists_channel(channel_id=channel_id):
                channel_db.delete_channel(channel_id=channel_id)
                await message.answer('Канал успешно удален')
            else:
                await message.answer('Такого канала нет!')


def register_handlers_sub_channel():
    admin_dp.register_message_handler(get_channel_id, commands='add_sub_channel', state=None)
    admin_dp.register_message_handler(get_channel_name, state=SubChannelFSM.get_channel_id)
    admin_dp.register_message_handler(set_sub_channel, state=SubChannelFSM)
    admin_dp.register_message_handler(delete_channel, commands='delete_channel')



