import paypalrestsdk

from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from create_bot.bot import dp
from databases.client_side import RegisterUserDB
from databases.payments import PayPalDB, VIP
from handlers.client_side.register_user import start_register
from keyboard.client_keyboard.inline.payments_paypal_keyboard import create_buy_vip_paypal_keyboard,\
    create_payment_vip_paypal_keyboard


async def create_payments(name, article, price, description):
    paypalrestsdk.configure({
        "mode": "sandbox",  # sandbox or live
        "client_id": "ARwutuygW1Fr9terIqi2MK9u2oBZ9orauA8KxvAuhSbvKj2NnDF3HD6ZrakR45fBHlDug87lYaSsgQwY",
        "client_secret": "EMt1HBWZqbVteeYnPz-SExUsLC3xUu2s76Y_IwGgK8vQiehcmEJHGCcF9iR2_MaVZdS_ejYmHfKwYLkV"})

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": f"{name}",
                    "sku": f"{article}",
                    "price": f"{price}.00",
                    "currency": "RUB",
                    "quantity": 1}]},
            "amount": {
                "total": f"{price}.00",
                "currency": "RUB"},
            "description": f"{description}"}]})

    if payment.create():
        print("Payment created successfully")
        payment_id = payment.id
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                return approval_url, payment_id
    else:
        return False, False


async def check_payment(payment_id: str):
    payment = paypalrestsdk.Payment.find(f'{payment_id}').to_dict()
    payer = payment.get('payer')
    if payer is not None:
        if payer.get('status') == 'VERIFIED':
            return payer
    return False


# @dp.message_handler(commands='vip')
async def create_payment(message: Message):
    if message.chat.type == 'private':
        register_db = RegisterUserDB()
        check_register_user = register_db.user_exists(user_id=message.from_user.id)
        if check_register_user:
            await message.answer('🔥 Получение <b>VIP!</b> 🔥\n\n'
                                 '📩Хотите получать доступ к диалогу с человеком? Вот она возможность! Приобретите VIP '
                                 'и сможете написать абсолютно любому человеку, который Вам понравится. Вы получите '
                                 'не просто доступ писать данному человеку, а <b>целый его аккаунт</b>!\n\n'
                                 '📹Хотите вставлять в профиль не только фото, но и <b>видео</b>? Со статусом VIP'
                                 ' Вы получите даже такую возможность\n\n'
                                 '👑Каждый человек, который имеет статус VIP <b>получает корону</b> в профиль\n\n'
                                 '🔥Не упусти возможность и <b>выделись</b>, приобретя статус VIP!',
                                 reply_markup=create_buy_vip_paypal_keyboard(33, 97, 200, 900), parse_mode='html')
        else:
            await start_register(message.from_user.id)


# @dp.callback_query_handler(Text(startswith='vip_paypal_'))
async def create_payments_one_day(callback: CallbackQuery):
    try:
        await callback.answer()
        type_vip = callback.data[len('vip_paypal_'):]
        text_payment = ''
        url = ''
        payments_id = 0
        time_vip = 0

        if type_vip == 'one_day':
            time_vip += 86400
            text_payment += 'Покупка 👑VIP👑 на 1 день'
            url, payments_id = await create_payments(name='Покупка VIP на 1 день', article='Buy VIP', price=33,
                                                     description='Покупка VIP на 1 день')
        elif type_vip == 'three_day':
            time_vip += 259200
            text_payment += 'Покупка 👑VIP👑 на 3 дня'
            url, payments_id = await create_payments(name='Покупка VIP на 3 дня', article='Buy VIP', price=97,
                                                     description='Покупка VIP на 3 дня')

        elif type_vip == 'week_day':
            time_vip += 604800
            text_payment += 'Покупка 👑VIP👑 на неделю'
            url, payments_id = await create_payments(name='Покупка VIP на неделю', article='Buy VIP', price=200,
                                                     description='Покупка VIP на неделю')

        elif type_vip == 'month_day':
            time_vip += 2592000
            text_payment += 'Покупка 👑VIP👑 на месяц!'
            url, payments_id = await create_payments(name='Покупка VIP на месяц', article='Buy VIP', price=900,
                                                     description='Покупка VIP на месяц')

        if url and payments_id:
            await callback.message.answer(text_payment,
                                          reply_markup=create_payment_vip_paypal_keyboard(url=url,
                                                                                          payment_id=payments_id,
                                                                                          days=time_vip))

    except Exception as ex:
        await callback.message.answer('Возникла неизвестная ошибка! Просьба обратиться к администрации')
        print(ex)


# @dp.callback_query_handler(Text(startswith=check_payment_ !{payment_id}_{days}))
async def check_payment_handler(callback: CallbackQuery):
    try:
        await callback.answer()
        data = callback.data.split('_')
        payment_id = data[2]
        time_vip = int(data[3])
        if await check_payment(payment_id=payment_id):
            paypal_db = PayPalDB()
            if not paypal_db.payment_exists(payments_id=payment_id):
                paypal_db.payment_add(user_id=callback.from_user.id, payments_id=payment_id)
                vip_db = VIP()
                vip_db.update_status_vip(user_id=callback.from_user.id, status_vip=True, time_vip=time_vip)
                await callback.message.answer('Поздравляем с приобретением статуса VIP!\n\n'
                                              'Теперь Вы являетесь исключительным пользователем данного бота\n\n'
                                              '<b>Новая команда</b>: "/statistic_vip"\n\n'
                                              '💫Желаем удачи💫', parse_mode='html')
            else:
                await callback.message.answer('Вы уже приобрели по данному платежи VIP!'
                                              ' Повторное приобретение - невозможно')
        else:
            await callback.message.answer('Платеж не найден')
    except Exception as ex:
        await callback.message.answer('Возникла неизвестная ошибка, если Вы приобрели VIP, но при этом '
                                      'возникает данная ошибка, то обратитесь к администратору!')
        print(ex)


def register_handlers_payments_paypal():
    dp.register_message_handler(create_payment, commands='vip')
    dp.register_message_handler(create_payment, Text(equals='VIP👑'))
    dp.register_callback_query_handler(create_payments_one_day, Text(startswith='vip_paypal_'))
    dp.register_callback_query_handler(check_payment_handler, Text(startswith='check_payment_'))
