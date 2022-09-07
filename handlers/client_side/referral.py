from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text

from create_bot.bot import dp
from create_bot.config import bot_name
from handlers.client_side.register_user import start_register
from databases.client_side import RegisterUserDB, ReferralDB
from keyboard.client_keyboard.inline.referral_keyboard import referral_menu
from utilits.translate_text import translate_from_lang_russian


# @dp.message_handler(commands='ref')
async def create_individual_referral(message: Message):
    if message.chat.type == 'private':
        register_db = RegisterUserDB()
        check_register_user = register_db.user_exists(user_id=message.from_user.id)
        if check_register_user:
            referral_text = f'За каждого приглашенного друга ты будешь получать баллы⭐️\n\n' \
                            f'Чем больше баллов - тем <b>⭐️выше шанс получить подарок⭐️</b>. <i>Даже VIP</i>!\n\n' \
                            f'Приглашая друзей ты увеличиваешь активность в боте и помогаешь чату!' \
                            f'Для получения баллов отправь друзьям <b>ссылку</b>:\n\n'
            translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                               text=referral_text)
            await message.answer(translate_text, parse_mode='html')
            await message.answer(f'👉 https://t.me/{bot_name}?start={message.from_user.id}\n\n',
                                 parse_mode='html', reply_markup=referral_menu)
        else:
            await start_register(message.from_user.id)


# @dp.callback_query_handler(Text(equals='statistic_referral'))
async def statistic_referral(callback: CallbackQuery):
    await callback.answer()
    referral_db = ReferralDB()
    amount_referral = referral_db.get_amount_referral(user_id=callback.from_user.id)
    statistic_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                       text=f'Количество баллов на данный момент: {amount_referral}\n\n'
                                                            f'Ссылка 👉'
                                                            f' https://t.me/{bot_name}?start={callback.from_user.id}')
    await callback.message.edit_text(text=statistic_text)
    translate_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                       text='Пригласите друзей и получите бесплатный VIP!')
    await callback.message.answer(translate_text)


def register_handlers_referral():
    dp.register_message_handler(create_individual_referral, commands='ref')
    dp.register_callback_query_handler(statistic_referral, Text(equals='statistic_referral'))

