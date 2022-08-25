import asyncio

import aioschedule

from aiogram import executor
from log.log import logger

from create_bot.bot import dp
from create_bot.commands import set_command
from utilits.notification_state_bot import notification_run
from utilits.deactivatet_user import deactivate
from utilits.update_top import update_top
from utilits.check_expiration_vip import check_expiration_vip


async def sheduler():
    aioschedule.every().day.at('12:00').do(deactivate)
    aioschedule.every().day.at('01:45').do(update_top)
    aioschedule.every(2).hours.do(check_expiration_vip)
    while 1:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def startup(_):
    logger.debug('START BOT')
    await notification_run()
    await set_command()
    asyncio.create_task(sheduler())


async def shutdown(_):
    pass


if __name__ == '__main__':
    from handlers import register_handlers
    executor.start_polling(dp, on_startup=startup, on_shutdown=shutdown, skip_updates=True)
