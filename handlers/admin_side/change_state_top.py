from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from create_bot.admin_bot import admin_dp
from create_bot.config import admins
from databases.admin_side import TopStateDB
from keyboard.admin_keyboard.inline.state_top_keyboard import state_top_menu
from log.log import logger


# @admin_dp.message_handler(commands='change_top')
async def choice_change_state_top(message: Message):
    if message.from_user.id in admins:
        await message.answer('Выберите один из ниже предложенных вариантов и бот все поменяет!',
                             reply_markup=state_top_menu)


# @admin_dp.callback_query_handler(Text(startswith='state_on_'))
async def change_state_top(callback: CallbackQuery):
    try:
        if callback.from_user.id in admins:
            state = callback.data[len('state_on_'):]
            top_state_db = TopStateDB()
            if state == 'top':
                top_state_db.set_state(state=False)
            elif state == 'king':
                top_state_db.set_state(state=True)
            await callback.answer('Успешно изменено!')
    except Exception as ex:
        logger.warning(f'При изменения состояния топа возникли ошибки у пользователя {callback.from_user.id}\n\n'
                       f'{ex}')


def register_handlers_change_state_top():
    admin_dp.register_message_handler(choice_change_state_top, commands='change_top')
    admin_dp.register_callback_query_handler(change_state_top, Text(startswith='state_on_'))
