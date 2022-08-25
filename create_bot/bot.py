import os
from asyncio import get_event_loop
from aiogram import Dispatcher, Bot
from create_bot.memory import memory
from create_bot.config import token


bot = Bot(token=token)
main_loop = get_event_loop()
dp = Dispatcher(bot=bot, loop=main_loop, storage=memory)
