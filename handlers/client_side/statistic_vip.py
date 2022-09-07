from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from create_bot.bot import dp
from databases.payments import VIP
from utilits.translate_text import translate_from_lang_russian


# @dp.message_handler(commands='statistic_vip')
async def get_statistic_vip(message: Message):
    if message.chat.type == 'private':
        vip_db = VIP()
        if vip_db.exists_user(user_id=message.from_user.id):
            remaining_time = vip_db.get_time(message.from_user.id)
            translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                               text=f'Вы являетесь пользователем VIP👑\n\n'
                                                                    f'✅Вам открыт полный доступ к командам и правам\n\n'
                                                                    f'Дата истечения VIP: <b>{remaining_time}</b> '
                                                                    f'(gmt+0)')
            await message.answer(translate_text, parse_mode='html')
        else:
            translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                               text='Вы не являетесь пользователем VIP!\n\n'
                                                                    'Ваши права ограничены')
            await message.answer(translate_text)


def register_handlers_statistic_vip():
    dp.register_message_handler(get_statistic_vip, commands='statistic_vip')
