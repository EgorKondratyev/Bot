import random

from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text

from create_bot.bot import dp
from handlers.client_side.register_user import start_register
from handlers.client_side.profile import get_attributes_user_for_profile
from handlers.client_side.payments_paypal import create_payments, check_payment
from databases.client_side import RegisterUserDB, TopDB
from databases.payments import KingChatDB
from keyboard.client_keyboard.inline.payments_paypal_keyboard import create_payment_king_chat_paypal_keyboard, \
    create_buy_king_chat_paypal_keyboard


# @dp.message_handler(commands='top👑')
# @dp.message_handler(Text(equals=['top', 'Топ', 'топ', 'Топ👑']))
async def get_top(message: Message):
    if message.chat.type == 'private':
        register_db = RegisterUserDB()
        check_register_user = register_db.user_exists(user_id=message.from_user.id)
        if check_register_user:
            top_text = f'Самые лучшие пользователи видны более <b>10 000 ежедневным участникам</b>' \
                       f' данного чат-бота для знакомств!\n\n'
            king_chat_db = KingChatDB()
            users_id = king_chat_db.get_users_id()  # ((user_id), (user_id))
            if users_id:
                phrase = ['Лучший из лучших!', 'Если человек не понимает твои мечты – он не твой человек',
                          'Лучшие люди приходят неожиданно',
                          'Мурлыканье кошек мне нравится больше чем пустые слова людей.',
                          'Совершенно разные, но при этом до невозможности близкие']
                for i, attribute_user in enumerate(users_id, 1):
                    user_id = attribute_user[0]
                    age, city, name_user, description_user, photo, instagram = await get_attributes_user_for_profile(
                        register_db=register_db, user_id=user_id)
                    top_text += f'{i}. 👉<a href="tg://user?id={user_id}">{name_user}</a> - {random.choice(phrase)}\n'
                top_text += '\nХочешь также? Тогда выгони из престола третьего участника и займи первое место!'
                await message.answer(top_text, reply_markup=create_buy_king_chat_paypal_keyboard(), parse_mode='html')
            else:
                top_text += f'Однако на данный момент никто не смог взять престол в свои руки! Будь же первым среди ' \
                            f'лучших'
                await message.answer(top_text, parse_mode='html', reply_markup=create_buy_king_chat_paypal_keyboard())
        else:
            await start_register(message.from_user.id)


# @dp.callback_query_handler(Text(startswith='king_chat_buy'))
async def create_king_payments(callback: CallbackQuery):
    price = 690
    king_chat_db = KingChatDB()
    if not king_chat_db.exists_user(callback.from_user.id):
        await callback.answer('Формируем платеж...')
        url, payment_id = await create_payments(name='Buy Place King Chat', article='king_chat', price=price,
                                                description='Buying the place of the king of chat and becoming'
                                                            ' the most popular')
        await callback.message.answer('Стать одним из королей чата - достойное дело!\n\n'
                                      'Ты будешь одним из самых популярных в этом чат боте для знакомств! \n\nТы готов?',
                                      reply_markup=create_payment_king_chat_paypal_keyboard(url, payment_id))

    else:
        await callback.answer()
        await callback.message.answer('Вы уже являетесь членом королевства!')


# @dp.callback_query_handler(Text(startswith='check_king_pay_'))
async def check_payment_king_chat(callback: CallbackQuery):
    try:
        await callback.answer('Проверяем платеж')
        king_chat_db = KingChatDB()
        if not king_chat_db.exists_user(callback.from_user.id):
            payment_id = callback.data[len('check_king_pay_'):]
            if await check_payment(payment_id):
                amount_users = len(king_chat_db.get_users_id())
                if amount_users < 3:
                    king_chat_db.add_user(user_id=callback.from_user.id)
                else:
                    delete_user_id = king_chat_db.get_users_id()[0][0]
                    king_chat_db.delete_user(delete_user_id)
                    king_chat_db.add_user(user_id=callback.from_user.id)
                await callback.message.answer('С этих пор Вы являетесь равноправным членом королевства!\n\n'
                                              'Благодарим за приобретение одного из мест на королевском троне')
            else:
                await callback.message.answer('Платеж не найден')
    except Exception as ex:
        await callback.message.answer('Возникла неизвестная ошибка! Просьба обратиться к администрации или заново '
                                      'сформировать платеж')

    # if message.chat.type == 'private':
    #     register_db = RegisterUserDB()
    #     check_register_user = register_db.user_exists(user_id=message.from_user.id)
    #     if check_register_user:
    #         top_db = TopDB()
    #         users = top_db.get_top_users()  # ((user_id, ...), (user_id...), )
    #         if users:
    #             top_text = '👑<b>Топ пользователей</b>👑\n\n'
    #             for i, user in enumerate(users, 1):
    #                 age, city, name_user, description_user, photo, instagram = await get_attributes_user_for_profile(
    #                     register_db=register_db, user_id=user[0])
    #                 top_text += f'{i}. 👉<a href="tg://user?id={user[0]}">{name_user}</a>\n' \
    #                             f'🥰Оценок: {user[1]}, 🔝рейтинг: {user[2]}\n\n'
    #
    #             top_text += f'Самые активные пользователи видны более <b>10 000 ежедневным участникам</b>' \
    #                         f' данного чат-бота для знакомств!'
    #
    #             await message.answer(top_text, parse_mode='html')
    #         else:
    #             await message.answer('На данный момент ни один из пользователей не был удостоен попасть в топ\n\n'
    #                                  'Стань же первым среди лучших!')
    #
    #     else:
    #         await start_register(message.from_user.id)


def register_handlers_top():
    dp.register_message_handler(get_top, commands='top')
    dp.register_message_handler(get_top, Text(equals=['top', 'Топ', 'топ', 'Топ👑']))
    dp.register_callback_query_handler(create_king_payments, Text(startswith='king_chat_buy'))
    dp.register_callback_query_handler(check_payment_king_chat, Text(startswith='check_king_pay_'))
