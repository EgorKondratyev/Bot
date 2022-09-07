from aiogram.types import Message

from create_bot.bot import bot, dp
from create_bot.config import admins
from databases.client_side import RegisterUserDB, ReferralDB
from databases.admin_side import NewsletterDB
from handlers.client_side.register_user import start_register
from keyboard.client_keyboard.default.main_keyboard import create_main_keyboard
from keyboard.admin_keyboard.inline.sub_channel import create_sub_channel_keyboard
from utilits.check_sub_channel import check_sub_channel
from utilits.translate_text import translate_from_lang_russian


# @dp.message_handler(commands='start')
async def start_command(message: Message):
    if message.chat.type == 'private':
        # Добавление в базу данных рассылки
        newsletter_db = NewsletterDB()
        if not newsletter_db.user_exists(user_id=message.from_user.id):
            newsletter_db.user_add(user_id=message.from_user.id)
        if await check_sub_channel(message.from_user.id):
            register_db = RegisterUserDB()
            if not register_db.user_exists(user_id=message.from_user.id):
                try:
                    referral_id = message.text[7:]
                    if referral_id:
                        referral_db = ReferralDB()
                        if not referral_db.referral_exists(message.from_user.id) and referral_id != message.from_user.id:
                            referral_db.referral_add(user_id=referral_id, referral=message.from_user.id)
                            amount_referral = referral_db.get_amount_referral(user_id=referral_id)
                            text_referral = f'⭐️Поздравляем⭐️\n\n' \
                                            f'Вы получили +1 балл за приглашенного друга!\n\n' \
                                            f'Теперь у Вас {amount_referral} балл(-ов)'
                            text_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                               text=text_referral)
                            await bot.send_message(referral_id, text_translate)
                except Exception:
                    pass

                await start_register(message.from_user.id)
            else:
                translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                   text='Тебя встречает уникальный бот для знакомств. '
                                                                        'Вам выданы все необходимые кнопки!')
                await message.answer(translate_text,
                                     reply_markup=await create_main_keyboard(message.from_user.id))
        else:
            text_channel_sub = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                 text='Прежде чем воспользоваться данным ботом'
                                                                      ' стоит подписаться на каналы!')
            await message.answer(text_channel_sub, reply_markup=create_sub_channel_keyboard())


# @dp.message_handler(commands='/help')
async def help_command(message: Message):
    if message.chat.type == 'private':
        text_help = 'Добро пожаловать в "поддержку" бота. Здесь Вы сможете узнать ответы на вопросы ' \
                    'или же связаться с администрацией\n\n' \
                    '"/help_lags" - если у Вас зависает бот или же плохо работает, то советуем обратиться ' \
                    'к данной команде\n\n' \
                    '"/help_administration" - команда для связи с администрацией (получение контактов)\n\n' \
                    'Приятного пользования нашим чат-ботом для знакомств🌌'

        if message.from_user.id in admins:
            text_help += '\n\nФункции для админов: \n\n' \
                         '1. "/add_fake_acc" - добавление фейкового аккаунта\n\n' \
                         '2. "/send_message" - рассылка\n\n' \
                         'Функции админов не отображаются для обычных пользователей'
        translate_text = await translate_from_lang_russian(message.from_user.id, text_help)
        await message.answer(translate_text)


# @dp.message_handler(commands='help_lags')
async def help_lags_command(message: Message):
    text_lags = 'Если у Вас происходят зависания или же что-либо долго погружается, то вероятнее всего дело в языке ' \
                'данный бот использует технологию "googletranslate", тем самым нам необходимо время для перевода ' \
                'исходного текста. Однако в нашем боте имеются несколько уже полностью переведенных языков, которые ' \
                'не должны зависать (английский и русский), чтобы сменить язык Вы можете заполнить заново профиль. ' \
                'Если после проделанных действий зависания продолжились (при смене на английский язык или русский), то ' \
                'обратитесь к администрации, мы постараемся Вам помочь!'
    translate_text = await translate_from_lang_russian(message.from_user.id, text_lags)
    await message.answer(translate_text)


async def get_administration(message: Message):
    user_id = 963249381
    text_admin = f'Администрация: <a href="tg://user?id={user_id}">Администратор</a>\n\n' \
                 f'Администрация: @dogersen\n\n'
    translate_text = await translate_from_lang_russian(message.from_user.id, text_admin)
    await message.answer(translate_text, parse_mode='html')


def register_start_handler():
    dp.register_message_handler(start_command, commands='start', state=None)
    dp.register_message_handler(help_command, commands='help')
    dp.register_message_handler(help_lags_command, commands='help_lags')
    dp.register_message_handler(get_administration, commands='help_administration')
