import paypalrestsdk

from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from create_bot.bot import dp
from databases.client_side import RegisterUserDB, LanguageDB
from databases.payments import PayPalDB, VIP, PriceDB
from databases.admin_side import PaypalSettingsDB
from handlers.client_side.register_user import start_register
from keyboard.client_keyboard.inline.payments_paypal_keyboard import create_buy_vip_paypal_keyboard, \
    create_payment_vip_paypal_keyboard
from utilits.translate_text import translate_from_lang_russian


async def create_payments(name, article, price, description):
    paypal_settings_db = PaypalSettingsDB()
    info = paypal_settings_db.get_client()
    if info:
        mode = ''
        client_id = ''
        client_secret = ''
        for attribute in info:
            client_id = attribute[0]
            client_secret = attribute[1]
            mode = attribute[2]
            if mode:
                mode = 'live'
            else:
                mode = 'sandbox'
        paypalrestsdk.configure({
            f"mode": f"{mode}",  # sandbox or live
            f"client_id": f"{client_id}",
            f"client_secret": f"{client_secret}"})
    else:
        return False, False

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "https://www.paypal.com/by/home",
            "cancel_url": "https://www.paypal.com/by/home"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": f"{name}",
                    "sku": f"{article}",
                    "price": f"{price}.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": f"{price}.00",
                "currency": "USD"},
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
            price_db = PriceDB()
            vip_text = '🔥 Получение <b>VIP!</b> 🔥\n\n' \
                       '📩Хотите получать доступ к диалогу с человеком? Вот она возможность! Приобретите VIP ' \
                       'и сможете написать абсолютно любому человеку, который Вам понравится. Вы получите ' \
                       'не просто доступ писать данному человеку, а <b>целый его аккаунт</b>!\n\n' \
                       '📹Хотите вставлять в профиль не только фото, но и <b>видео</b>? Со статусом VIP' \
                       ' Вы получите даже такую возможность\n\n' \
                       '👑Каждый человек, который имеет статус VIP <b>получает корону</b> в профиль\n\n' \
                       '🔥Не упусти возможность и <b>выделись</b>, приобретя статус VIP!'

            language_db = LanguageDB()

            language = language_db.get_language_user(user_id=message.from_user.id)

            if language == 'ar':
                translate_vip_text = '🔥الحصول على كبار الشخصيات!🔥\n\n' \
                                     '📩هل تريد الوصول إلى حوار مع شخص? هنا فرصة! شراء كبار الشخصيات' \
                                     'ويمكنك الكتابة إلى أي شخص تحبه على الإطلاق. سوف تتلقى ' \
                                     'ليس فقط الوصول للكتابة إلى هذا الشخص ، ولكن حسابه كله\n\n' \
                                     '📹هل تريد إدراج ليس فقط الصور, ولكن أيضا مقاطع الفيديو في ملفك الشخصي? مع حالة كبار الشخصيات '
            else:
                translate_vip_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                       text=vip_text)
            await message.answer(translate_vip_text,
                                 reply_markup=await create_buy_vip_paypal_keyboard(
                                     price_db.get_one_day_price(),
                                     price_db.get_three_day_price(),
                                     price_db.get_week_day_price(),
                                     price_db.get_month_day_price(),
                                     user_id=message.from_user.id), parse_mode='html')
        else:
            await start_register(message.from_user.id)


# @dp.callback_query_handler(Text(startswith='vip_paypal_'))
async def create_payments_one_day(callback: CallbackQuery):
    try:
        await callback.answer()
        price_db = PriceDB()
        type_vip = callback.data[len('vip_paypal_'):]
        text_payment = ''
        url = ''
        payments_id = 0
        time_vip = 0

        if type_vip == 'one_day':
            time_vip += 86400
            price = price_db.get_one_day_price()
            text_payment = 'Покупка 👑VIP👑 на 1 день'
            text_payment = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                             text=text_payment)
            url, payments_id = await create_payments(name='Покупка VIP на 1 день', article='Buy VIP', price=price,
                                                     description='Покупка VIP на 1 день')
        elif type_vip == 'three_day':
            time_vip += 259200
            price = price_db.get_three_day_price()
            text_payment += 'Покупка 👑VIP👑 на 3 дня'
            text_payment = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                             text=text_payment)
            url, payments_id = await create_payments(name='Покупка VIP на 3 дня', article='Buy VIP', price=price,
                                                     description='Покупка VIP на 3 дня')

        elif type_vip == 'week_day':
            time_vip += 604800
            price = price_db.get_week_day_price()
            text_payment += 'Покупка 👑VIP👑 на неделю'
            text_payment = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                             text=text_payment)
            url, payments_id = await create_payments(name='Покупка VIP на неделю', article='Buy VIP', price=price,
                                                     description='Покупка VIP на неделю')

        elif type_vip == 'month_day':
            time_vip += 2592000
            price = price_db.get_month_day_price()
            text_payment += 'Покупка 👑VIP👑 на месяц!'
            text_payment = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                             text=text_payment)
            url, payments_id = await create_payments(name='Покупка VIP на месяц', article='Buy VIP', price=price,
                                                     description='Покупка VIP на месяц')

        if url and payments_id:
            await callback.message.answer(text_payment,
                                          reply_markup=
                                          await create_payment_vip_paypal_keyboard(url=url,
                                                                                   payment_id=payments_id,
                                                                                   days=time_vip,
                                                                                   user_id=callback.from_user.id))

    except Exception as ex:
        text_error = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                       text='Возникла неизвестная ошибка!'
                                                            ' Просьба обратиться к администрации')
        await callback.message.answer(text_error)


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
                successful_buy_vip_text = 'Поздравляем с приобретением статуса VIP!\n\n' \
                                          'Теперь Вы являетесь исключительным пользователем данного бота\n\n' \
                                          '<b>Новая команда</b>: "/statistic_vip"\n\n' \
                                          '💫Желаем удачи💫'
                translate_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                                   text=successful_buy_vip_text)
                await callback.message.answer(translate_text, parse_mode='html')
            else:
                replay_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                                text='Вы уже приобрели по данному платежи VIP!'
                                                                     ' Повторное приобретение - невозможно')
                await callback.message.answer(replay_text)
        else:
            text_payment_not_found = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                                       text='Платеж не найден')
            await callback.message.answer(text_payment_not_found)
    except Exception as ex:
        error_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                       text='Возникла неизвестная ошибка, если Вы приобрели VIP,'
                                                            ' но при этом возникает данная ошибка,'
                                                            ' то обратитесь к администратору!')
        await callback.message.answer(error_text)
        print(ex)


def register_handlers_payments_paypal():
    dp.register_message_handler(create_payment, commands='vip')
    dp.register_message_handler(create_payment, Text(equals='VIP👑'))
    dp.register_callback_query_handler(create_payments_one_day, Text(startswith='vip_paypal_'))
    dp.register_callback_query_handler(check_payment_handler, Text(startswith='check_payment_'))
