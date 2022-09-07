from aiogram.types import Message

from create_bot.bot import bot
from create_bot.admin_bot import admin_dp
from create_bot.config import admins
from databases.client_side import LanguageDB, RegisterUserDB
from databases.admin_side import ComplainsDB, NewsletterDB


# @admin_dp.message_handler(commands=['statistic'])
async def statistic_base(message: Message):
    if message.from_user.id in admins and message.chat.type == 'private':
        newsletter_db = NewsletterDB()
        language_db = LanguageDB()
        register_db = RegisterUserDB()

        amount_users = len(newsletter_db.get_users_id())
        amount_register_user_id = len(register_db.get_all_user_id())
        amount_active_user_id = len(register_db.get_all_user_id_by_true_active())
        languages = language_db.get_all_language()

        english_amount = 0
        russian_amount = 0
        ukrainian_amount = 0
        arabic_amount = 0
        belarusian_amount = 0
        german_amount = 0
        polish_amount = 0
        italian_amount = 0
        japanese_amount = 0

        for attribute_language in languages:
            language = attribute_language[0]
            match language:
                case 'en':
                    english_amount += 1
                case 'ru':
                    russian_amount += 1
                case 'uk':
                    ukrainian_amount += 1
                case 'ar':
                    arabic_amount += 1
                case 'be':
                    belarusian_amount += 1
                case 'de':
                    german_amount += 1
                case 'pl':
                    polish_amount += 1
                case 'it':
                    italian_amount += 1
                case 'ja':
                    japanese_amount += 1

        await message.answer(f'Пользователей в боте (за все время): {amount_users}\n'
                             f'Зарегистрированных пользователей: {amount_register_user_id}\n'
                             f'Активных пользователей: {amount_active_user_id}\n\n'
                             f'Статистика по языкам: \n'
                             f'1. Английский: {english_amount}\n'
                             f'2. Русский: {russian_amount}\n'
                             f'3. Украинский: {ukrainian_amount}\n'
                             f'4. Арабский: {arabic_amount}\n'
                             f'5. Белорусский: {belarusian_amount}\n'
                             f'6. Немецкий: {german_amount}\n'
                             f'7. Польский: {polish_amount}\n'
                             f'8. Итальянский: {italian_amount}\n'
                             f'9. Японский: {japanese_amount}')
        await message.answer('Пометка: боты входят в зарегистрированных пользователей, но при этом активными '
                             'не являются. В некоторых случаях бот может являться активным пользователем (в результате '
                             'какого-либо вмешательства')


async def statistic_complain(message: Message):
    if message.from_user.id in admins and message.chat.type == 'private':
        complain_db = ComplainsDB()
        info = complain_db.get_all_info()
        if info:
            top_complains = [(123456, 0), (123456, 0), (123456, 0), (123456, 0), (123456, 0)]
            await message.answer('Отображается топ 5 пользователей, на которых поступают жалобы')
            for attribute in info:
                user_id = attribute[0]
                amount_complains = attribute[1]
                if amount_complains > top_complains[0][1]:
                    top_complains[0] = (user_id, amount_complains)
                    continue
                elif amount_complains > top_complains[1][1]:
                    top_complains[1] = (user_id, amount_complains)
                    continue
                elif amount_complains > top_complains[2][1]:
                    top_complains[2] = (user_id, amount_complains)
                    continue
                elif amount_complains > top_complains[3][1]:
                    top_complains[3] = (user_id, amount_complains)
                    continue
                elif amount_complains > top_complains[4][1]:
                    top_complains[4] = (user_id, amount_complains)
                    continue
            top_text = ''
            iteration = 0
            for attribute in top_complains:
                if attribute != (123456, 0):
                    try:
                        info = await bot.get_chat(attribute[0])
                        await message.answer(f'Пользователь с ID {info.id}\n'
                                             f'Не числовой: @{info.username}\n'
                                             f'Получил {attribute[1]} жалоб')
                        iteration += 1
                    except Exception:
                        pass
            if iteration == 0:
                await message.answer('На данный момент нет пользователей, на которых бы поступала жалоба')
        else:
            await message.answer('На данный момент нет пользователей, на которых бы поступала жалоба')


def register_handlers_statistic():
    admin_dp.register_message_handler(statistic_base, commands='statistic')
    admin_dp.register_message_handler(statistic_complain, commands='statistic_complain')
