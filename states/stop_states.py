from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.dispatcher.filters import Text

from create_bot.bot import dp
from create_bot.config import admins


# @dp.message_handler(commands='stop', state='*')
# @dp.message_handler(Text(equals=['stop', 'стоп'], ignore_case=True), state='*')
async def stop_states(message: Message, state: FSMContext):
    if message.chat.type == 'private' and message.from_user.id in admins:
        current_state = await state.get_state()
        if current_state is None:
            await message.answer('Останавливать нечего!')
            return
        await state.finish()
        await message.answer('Операция успешно остановлена')


def register_stop_handlers():
    dp.register_message_handler(stop_states, commands='stop', state='*')
    dp.register_message_handler(stop_states, Text(equals=['stop', 'стоп'], ignore_case=True), state='*')
