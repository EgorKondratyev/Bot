from aiogram import executor

from create_bot.admin_bot import admin_dp

if __name__ == '__main__':
    from handlers import register_admin_handlers
    executor.start_polling(admin_dp, skip_updates=True)
