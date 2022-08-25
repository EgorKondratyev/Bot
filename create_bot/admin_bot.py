from asyncio import get_event_loop
from aiogram import Dispatcher, Bot
from create_bot.memory import memory
from create_bot.config import token_admin as token


admin_bot = Bot(token=token)
main_loop = get_event_loop()
admin_dp = Dispatcher(bot=admin_bot, loop=main_loop, storage=memory)
