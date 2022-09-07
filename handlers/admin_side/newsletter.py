from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from create_bot.bot import bot, dp as admin_dp
from create_bot.config import admins
from databases.admin_side import NewsletterDB
from keyboard.admin_keyboard.inline.newsletter_keyboard import menu_confrim
from states.admin_states.newsletter_states import NewsletterFSM
from log.log import logger


# @admin_dp.message_handler(commands='send_message', state=None)
async def getting_message(message: Message):
    if message.from_user.id in admins:
        await message.answer('Меню рассылки\n\n'
                             'Отправь мне сообщение, которое хотел бы разослать другим пользователям: ')
        await NewsletterFSM.get_message.set()
        await message.answer('Для остановки напишите "stop"')


# @admin_dp.message_handler(state=NewsletterFSM.get_message, content_types='any')
async def confirm_send_message(message: Message, state: FSMContext):
    if message.video:
        file_id = message.video.file_id
        if message.caption is not None:
            message_owner = message.caption
        else:
            message_owner = ''

        await message.answer_video(video=message.video.file_id,
                                   caption=f'Вот Ваше рассылочное сообщение:\n\n'
                                           f'{message_owner}', reply_markup=menu_confrim)
        async with state.proxy() as data:
            data['text'] = message_owner
            data['photo'] = 0
            data['video'] = file_id
    elif message.photo:
        file_id = message.photo[-1].file_id
        print(file_id)
        if message.caption is not None:
            message_owner = message.caption
        else:
            message_owner = ''

        await message.answer_photo(photo=file_id,
                                   caption=f'Вот Ваше рассылочное сообщение:\n\n'
                                           f'{message_owner}', reply_markup=menu_confrim)
        async with state.proxy() as data:
            data['text'] = message_owner
            data['photo'] = file_id
            data['video'] = 0
    elif message.text is not None:
        if message.text == 'stop':
            await state.finish()
            await message.answer('OK')
            return
        message_owner = message.text
        await message.answer('Вот Ваше рассылочное сообщение:\n\n'
                             f'{message_owner}', reply_markup=menu_confrim)

        async with state.proxy() as data:
            data['text'] = message_owner
            data['photo'] = 0
            data['video'] = 0
    await NewsletterFSM.go_newsletter.set()


# @admin_dp.callback_query_handler(Text(equals='go_newsletter'), state=NewsletterFSM.go_newsletter)
async def newsletter(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'go_newsletter_stop':
        await state.finish()
        await callback.message.answer('OK')
        return
    await callback.answer('Начинаю рассылку...')
    owner_video = 0
    owner_photo = 0
    owner_text = ''

    async with state.proxy() as data:
        if data['video']:
            owner_video = data['video']
            owner_text = data['text']

        elif data['photo']:
            owner_photo = data['photo']
            owner_text = data['text']

        elif data['text']:
            owner_text = data['text']
    await state.finish()
    newsletter_db = NewsletterDB()
    users_id = newsletter_db.get_users_id()
    if users_id:
        if owner_video:
            for attribute_user in users_id:
                try:
                    user_id = attribute_user[0]
                    await bot.send_video(chat_id=user_id, video=owner_video, caption=owner_text)
                    logger.debug(f'Пользователь {user_id} успешно получил рассылочное сообщение')
                except Exception as ex:
                    logger.warning(f'Ошибка при рассылке видео\n\n'
                                   f'{ex}')
        elif owner_photo:
            for attribute_user in users_id:
                try:
                    user_id = attribute_user[0]
                    print(owner_photo)
                    await bot.send_photo(chat_id=user_id, photo=owner_photo, caption=owner_text)
                    logger.debug(f'Пользователь {user_id} успешно получил рассылочное сообщение')
                except Exception as ex:
                    logger.warning(f'Ошибка при рассылке видео\n\n'
                                   f'{ex}')
        elif owner_text:
            for attribute_user in users_id:
                try:
                    user_id = attribute_user[0]
                    await bot.send_message(chat_id=user_id, text=owner_text)
                    logger.debug(f'Пользователь {user_id} успешно получил рассылочное сообщение')
                except Exception as ex:
                    logger.warning(f'Ошибка при рассылке видео\n\n'
                                   f'{ex}')
    else:
        pass

    await callback.message.answer('Успешно разосланы все сообщения!🥳🥳')


def register_handlers_newsletter():
    admin_dp.register_message_handler(getting_message, commands='send_message', state=None)
    admin_dp.register_message_handler(confirm_send_message, state=NewsletterFSM.get_message, content_types='any')
    admin_dp.register_callback_query_handler(newsletter, Text(startswith='go_newsletter'),
                                             state=NewsletterFSM.go_newsletter)
