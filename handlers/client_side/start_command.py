from aiogram.types import Message

from create_bot.bot import bot, dp
from databases.client_side import RegisterUserDB, ReferralDB
from handlers.client_side.register_user import start_register
from keyboard.client_keyboard.default.main_keyboard import main_menu


# @dp.message_handler(commands='start')
async def start_command(message: Message):
    if message.chat.type == 'private':
        register_db = RegisterUserDB()
        if not register_db.user_exists(user_id=message.from_user.id):
            try:
                referral_id = message.text[7:]
                if referral_id:
                    referral_db = ReferralDB()
                    if not referral_db.referral_exists(message.from_user.id) and referral_id != message.from_user.id:
                        referral_db.referral_add(user_id=referral_id, referral=message.from_user.id)
                        amount_referral = referral_db.get_amount_referral(user_id=referral_id)
                        await bot.send_message(referral_id, f'⭐️Поздравляем⭐️\n\n'
                                                            f'Вы получили +1 балл за приглашенного друга!\n\n'
                                                            f'Теперь у Вас {amount_referral} балл(-ов)')
            except Exception:
                pass

            await start_register(message.from_user.id)
        else:
            await message.answer('И снова мы встретились!', reply_markup=main_menu)


def register_start_handler():
    dp.register_message_handler(start_command, commands='start', state=None)
