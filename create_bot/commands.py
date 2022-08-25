from aiogram.types.bot_command import BotCommand

from create_bot.bot import bot


async def set_command():
    commands = [
        BotCommand(command='start', description='Получение стартовых кнопок'),
        BotCommand(command='profile', description='Ваш профиль'),
        BotCommand(command='search', description='🚀Просмотр анкет'),
        BotCommand(command='ref', description='📈Пригласить друзей'),
        BotCommand(command='top', description='👑Просмотр топа')
    ]
    await bot.set_my_commands(commands)
