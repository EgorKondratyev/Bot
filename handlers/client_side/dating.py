import random
import time

from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BadRequest

from create_bot.bot import dp
from databases.client_side import RegisterUserDB, ScoresDB, StatisticDB
from databases.admin_side import ComplainsDB, BanUsersDB
from databases.payments import VIP
from handlers.client_side.register_user import start_register
from handlers.client_side.profile import get_attributes_user_for_profile
from keyboard.client_keyboard.inline.dating_keyboard import scores, update_scores, complain_menu
from log.log import logger
from utilits.check_sub_channel import check_sub_channel
from utilits.translate_text import translate_from_lang_russian
from keyboard.admin_keyboard.inline.sub_channel import create_sub_channel_keyboard


async def get_attributes_user_for_dating(register_db, user_id):
    """Получение аттрибутов:user_sex, interesting_sex"""
    info = register_db.get_all_info_by_user_id(user_id=user_id)  # ((user_id, status, age...),)
    for attributes_user in info:
        user_sex = attributes_user[4]
        interesting_sex = attributes_user[5]
        return user_sex, interesting_sex


# @dp.message_handler(Text(equals=['Смотреть анкеты🚀']))
async def questionnaire_review(message: Message):
    if message.chat.type == 'private':
        try:
            if await check_sub_channel(message.from_user.id):
                ban_db = BanUsersDB()
                if not ban_db.exists_user(user_id=message.from_user.id):
                    register_db = RegisterUserDB()
                    check_register_user = register_db.user_exists(user_id=message.from_user.id)
                    if check_register_user:
                        user_sex, interesting_sex = await get_attributes_user_for_dating(register_db,
                                                                                         user_id=message.from_user.id)
                        users_id = register_db.get_users_id_by_interesting_sex(user_sex=user_sex,
                                                                               interesting_sex=interesting_sex)
                        evaluated_users_id = register_db.get_evaluated_users(user_id=message.from_user.id)
                        while 1:
                            if users_id and len(users_id) != 1:
                                user_id = random.choice(users_id)
                                if user_id not in evaluated_users_id and user_id != message.from_user.id:
                                    age, city, name_user, description_user, photo, instagram = await \
                                        get_attributes_user_for_profile(register_db=register_db, user_id=user_id)
                                    vip_db = VIP()
                                    if vip_db.exists_user(user_id=user_id):
                                        caption = f'{name_user}, {age}, {city} 👑\n\n'
                                    else:
                                        caption = f'{name_user}, {age}, {city}\n\n'
                                    if instagram is None:
                                        caption += f'{description_user}'
                                    else:
                                        if description_user:
                                            caption = f'{description_user}\n\n' \
                                                      f'<b>instagram</b>: <code>{instagram}</code>'
                                        else:
                                            caption = f'<b>instagram</b>: <code>{instagram}</code>'
                                    try:
                                        await message.answer_photo(photo=photo, caption=caption,
                                                                   reply_markup=scores(user_id=user_id), parse_mode='html')
                                    except BadRequest:
                                        await message.answer_video(video=photo, caption=caption,
                                                                   reply_markup=scores(user_id=user_id), parse_mode='html')
                                    register_db.add_evaluated(message.from_user.id, evaluated_id=user_id)
                                    # На каждое действие update UNIX time
                                    register_db.update_unix_time(user_id=message.from_user.id, unix_time=int(time.time()))
                                    register_db.update_active(active=True, user_id=message.from_user.id)
                                    break
                                elif user_id == message.from_user.id:
                                    pass
                                else:
                                    try:
                                        evaluated_users_id.remove(user_id)
                                        register_db.delete_evaluated(user_id=message.from_user.id, evaluated_id=user_id)
                                    except Exception as ex:
                                        logger.debug(f'{ex} {user_id}')
                            else:
                                text_translate = \
                                    await translate_from_lang_russian(user_id=message.from_user.id,
                                                                      text='На данный момент нет ни одного пользователя, '
                                                                           'который подходит Вам!')
                                await message.answer(text_translate)
                                break
                    else:
                        await start_register(message.from_user.id)
                else:
                    translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                       text='Вы находитесь в блокировке')
                    await message.answer(translate_text)
            else:
                text_channel_sub = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                     text='Прежде чем воспользоваться данным ботом'
                                                                          ' стоит подписаться на каналы!')
                await message.answer(text_channel_sub, reply_markup=create_sub_channel_keyboard())
        except Exception as ex:
            # Ошибки будут достаточно типичны и в большинстве своем адекватны для данного кода. К примеру: user_id
            # зачастую будет совпадать с message.from_user.id, сделано для того, дабы минимизировать нагрузку
            logger.debug(f'Возникла ошибка при просмотре анкет у пользователя {message.from_user.id}\n'
                         f'{ex}')


# @dp.callback_query_handler(Text(startswith='score'))
async def score_and_next_review(callback: CallbackQuery):
    await callback.answer()
    try:
        if await check_sub_channel(callback.from_user.id):
            ban_db = BanUsersDB()
            if not ban_db.exists_user(user_id=callback.from_user.id):
                user_id = callback.data[9:]
                smile = callback.data[6:8]

                await callback.message.edit_reply_markup(reply_markup=update_scores(smile, evaluated_id=user_id))
                scores_db = ScoresDB()
                statistic_db = StatisticDB()
                # Добавление в "мои отметки"
                if not scores_db.exists_my_score(user_id=callback.from_user.id, evaluated_id=user_id):
                    scores_db.add_my_score(user_id=callback.from_user.id, smile=smile, evaluated_id=user_id)

                statistic_db.increment_my_scores(user_id=callback.from_user.id)
                statistic_db.increment_their_scores(user_id=user_id)

                # Добавление в отметки того пользователя, которого мы оценили "мои оценки"
                if not scores_db.exists_their_score(user_id=user_id, evaluated_id=callback.from_user.id):
                    scores_db.add_their_score(user_id=user_id, smile=smile, evaluated_id=callback.from_user.id)
                register_db = RegisterUserDB()
                check_register_user = register_db.user_exists(user_id=callback.from_user.id)
                if check_register_user:
                    user_sex, interesting_sex = await get_attributes_user_for_dating(register_db,
                                                                                     user_id=callback.from_user.id)
                    users_id = register_db.get_users_id_by_interesting_sex(user_sex=user_sex,
                                                                           interesting_sex=interesting_sex)
                    evaluated_users_id = register_db.get_evaluated_users(user_id=callback.from_user.id)
                    while 1:
                        if users_id:
                            user_id = random.choice(users_id)
                            if user_id not in evaluated_users_id and user_id != callback.from_user.id:
                                age, city, name_user, description_user, photo, instagram = await \
                                    get_attributes_user_for_profile(register_db=register_db, user_id=user_id)
                                vip_db = VIP()
                                if vip_db.exists_user(user_id=user_id):
                                    caption = f'{name_user}, {age}, {city} 👑\n\n'
                                else:
                                    caption = f'{name_user}, {age}, {city}\n\n'
                                if instagram is None:
                                    caption += f'{description_user}'
                                else:
                                    if description_user:
                                        caption = f'{description_user}\n\n' \
                                                  f'<b>instagram</b>: <code>{instagram}</code>'
                                    else:
                                        caption = f'<b>instagram</b>: <code>{instagram}</code>'
                                try:
                                    print(user_id)
                                    await callback.message.answer_photo(photo=photo, caption=caption,
                                                                        reply_markup=scores(user_id=user_id),
                                                                        parse_mode='html')
                                    print(1)
                                except BadRequest:
                                    print(user_id)
                                    await callback.message.answer_video(video=photo, caption=caption,
                                                                        reply_markup=scores(user_id=user_id),
                                                                        parse_mode='html')
                                    print(2)
                                register_db.add_evaluated(callback.from_user.id, evaluated_id=user_id)
                                # На каждое действие update UNIX time
                                register_db.update_unix_time(user_id=callback.from_user.id, unix_time=int(time.time()))
                                register_db.update_active(active=True, user_id=callback.from_user.id)
                                break
                            elif user_id == callback.from_user.id:
                                pass
                            else:
                                try:
                                    evaluated_users_id.remove(user_id)
                                    register_db.delete_evaluated(user_id=callback.from_user.id, evaluated_id=user_id)
                                except Exception as ex:
                                    logger.debug(f'{ex}  {user_id}')
                else:
                    await start_register(callback.from_user.id)
            else:
                translate_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                                   text='Вы находитесь в блокировке')
                await callback.message.answer(translate_text)
        else:
            text_channel_sub = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                                 text='Прежде чем воспользоваться данным ботом'
                                                                      ' стоит подписаться на каналы!')
            await callback.message.answer(text_channel_sub, reply_markup=create_sub_channel_keyboard())
    except Exception as ex:
        logger.debug(f'Возникла ошибка при оценке анкет у пользователя {callback.from_user.id}\n'
                     f'{ex}')


# @dp.callback_query_handler(Text(equals='complain_on_user'))
async def complain_handler(callback: CallbackQuery):
    complain_db = ComplainsDB()
    # В статистику встраивались и жалобы (хотя казалось бы можно взять и из complain_db) так как учитываются и
    # жалобы, которые кидают НА пользователя
    statistic_db = StatisticDB()
    user_id = callback.data[len('complain_on_user_'):]
    complain_db.increment_complains(user_id=user_id)
    statistic_db.increment_amount_my_complain(user_id=callback.from_user.id)
    statistic_db.increment_amount_their_complain(user_id=user_id)
    complain_text = await translate_from_lang_russian(user_id=callback.from_user.id, text='Жалоба успешно отправлена')
    await callback.answer(complain_text)
    await callback.message.edit_reply_markup(reply_markup=complain_menu)


# @dp.callback_query_handler(Text(equals='write_user'))
async def write_to_the_user(callback: CallbackQuery):
    vip_db = VIP()
    if vip_db.exists_user(user_id=callback.from_user.id):
        register_db = RegisterUserDB()
        user_id = callback.data[len('write_user_'):]
        await callback.answer()
        age, city, name_user, description_user, photo, instagram = await \
            get_attributes_user_for_profile(register_db=register_db, user_id=user_id)
        good_time_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                           text='Надеюсь ты хорошо проведешь время!')
        await callback.message.answer(text=good_time_text +
                                      f'\n\n👉<a href="tg://user?id={user_id}">{name_user}</a>', parse_mode='html')
        warning_text = 'Если по каким-либо причинам ссылка неактивна, то вероятнее всего аккаунт ' \
                       'был удален или же по неизвестным причинам доступ был к нему ограничен'
        translate_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                           text=warning_text)
        await callback.message.answer(translate_text)
    else:
        no_vip_text = 'У Вас нет статуса VIP! Данная функция доступна только при получении ' \
                      'статуса VIP\n\n' \
                      '"/vip" - приобрести VIP👑'
        translate_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                           text=no_vip_text)
        await callback.message.answer(translate_text)


def register_dating_handlers():
    dp.register_message_handler(questionnaire_review, Text(startswith='🚀'))
    dp.register_message_handler(questionnaire_review, commands='search')
    dp.register_callback_query_handler(score_and_next_review, Text(startswith='score'))
    dp.register_callback_query_handler(complain_handler, Text(startswith='complain_on_user'))
    dp.register_callback_query_handler(write_to_the_user, Text(startswith='write_user'))
