import os
from dotenv import load_dotenv

from create_bot.bot import bot, dp
from log.log import logger


async def notification_run():
    """Оповещение админов о запуске бота"""
    load_dotenv()
    admins = list(map(int, os.getenv("ADMINS").split(',')))
    for admin in admins:
        await bot.send_message(chat_id=admin, text='Бот успешно запущен')
        logger.debug(f'Администратор {admin} оповещён')
