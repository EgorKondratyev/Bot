from aiogram.types import Message

from create_bot.admin_bot import admin_dp
from create_bot.config import admins


# @admin_dp.message_handler(commands=['start', 'help'])
async def start_command(message: Message):
    if message.from_user.id in admins:
        await message.answer('Приветствую Вас, многоуважаемый админ. Вы вольны творить много с этим ботом, '
                             'изменять цены, менять топы, менять судьбы своих пользователей!\n'
                             'Пользуйтесь дарованными привилегиями с умом и осторожностью\n'
                             'Все доступные Вам функции: \n\n'
                             '1. "/change_price" - изменение цен продуктов. Можно изменить цену на абсолютно любой '
                             'продукт!\n'
                             '2. "/add_sub_channel" - какой-то канал захотел дать Вам денег, но взамен просит рекламу '
                             'через бота? - Не проблема! Просто добавь сюда бота и следуй каждому слову при'
                             ' добавлении\n'
                             '3. "/delete_channel" - истек контракт? Не хотят давать деньги? - просто удали его из '
                             'базы данных бота\n'
                             '4. "/change_top" - хочешь изменить топ на собственное королевство, в котором тебе будут '
                             'платить дань? - Не проблема, бери и меняй!\n'
                             '5. "/issuance_king" - выдача статуса короля\n'
                             '6. "/issuance_vip" - выдача VIP\n'
                             '7. "/statistic" - статистика по пользователям (общая)\n'
                             '8. "/ban_users" - забанить пользователя\n'
                             '9. "/unban_users" - разбанить пользователя\n'
                             '10. "/settings_gift" - настройка подарка при подписке\n'
                             '11. "/paypal_settings" - изменение mode, client id и secret Вашего paypal в боте\n'
                             '\n\nНекоторые из команд также доступны при команде "/help" в боте'
                             )


def register_handler_start_command():
    admin_dp.register_message_handler(start_command, commands=['start', 'help'])
