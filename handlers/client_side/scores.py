# Модуль отвечающий за команды "меня оценили" и "мои оценки"

from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from create_bot.bot import dp
from handlers.client_side.profile import get_attributes_user_for_profile
from keyboard.client_keyboard.inline.dating_keyboard import update_scores
from databases.client_side import ScoresDB, RegisterUserDB


# @dp.message_handler(Text(startswith=['меня оценили']))
async def i_was_evaluated(message: Message):
    if message.chat.type == 'private':
        register_db = RegisterUserDB()
        check_register_user = register_db.user_exists(user_id=message.from_user.id)
        if check_register_user:
            scores_db = ScoresDB()
            their_scores = scores_db.get_their_scores(user_id=message.from_user.id)
            print(their_scores)
            if their_scores:
                not_rated = 0
                for user_id in their_scores:
                    evaluated_id = user_id[0]
                    if evaluated_id is not None:  # Если мы оценили пользователя, а он нас нет, то будет None
                        smile = scores_db.get_smile(user_id=message.from_user.id, evaluated_id=evaluated_id)
                        age, city, name_user, description_user, photo, instagram = await \
                            get_attributes_user_for_profile(register_db=register_db, user_id=evaluated_id)
                        if instagram is None:
                            caption = f'{name_user}, {age}, {city}\n\n' \
                                      f'{description_user}'
                        else:
                            if description_user:
                                caption = f'{name_user}, {age}, {city}\n\n' \
                                          f'{description_user}\n\n' \
                                          f'<b>instagram</b>: <code>{instagram}</code>'
                            else:
                                caption = f'{name_user}, {age}, {city}\n\n' \
                                          f'<b>instagram</b>: <code>{instagram}</code>'
                        await message.answer_photo(photo=photo, caption=caption, parse_mode='html',
                                                   reply_markup=update_scores(score=smile, evaluated_id=evaluated_id))
                        not_rated += 1
                    else:
                        pass
                if not_rated == 0:
                    await message.answer('На данный момент Вас никто не оценил\n\n'
                                         'Самое время воспользоваться командой "/search" и набрать свою популярность!')
            else:
                await message.answer('На данный момент Вас никто не оценил\n\n'
                                     'Самое время воспользоваться командой "/search" и набрать свою популярность!')


# @dp.message_handler(Text(startswith='мои отметки'))
async def my_score(message: Message):
    if message.chat.type == 'private':
        register_db = RegisterUserDB()
        check_register_user = register_db.user_exists(user_id=message.from_user.id)
        if check_register_user:
            scores_db = ScoresDB()
            my_scores = scores_db.get_my_score(user_id=message.from_user.id)
            if my_scores:
                not_rated = 0
                for user_id in my_scores:
                    evaluated_id = user_id[0]
                    if evaluated_id is not None:  # Если мы оценили пользователя, а он нас нет, то будет None
                        smile = scores_db.get_smile(user_id=message.from_user.id, evaluated_id=evaluated_id)
                        age, city, name_user, description_user, photo, instagram = await \
                            get_attributes_user_for_profile(register_db=register_db, user_id=evaluated_id)
                        if instagram is None:
                            caption = f'{name_user}, {age}, {city}\n\n' \
                                      f'{description_user}'
                        else:
                            if description_user:
                                caption = f'{name_user}, {age}, {city}\n\n' \
                                          f'{description_user}\n\n' \
                                          f'<b>instagram</b>: <code>{instagram}</code>'
                            else:
                                caption = f'{name_user}, {age}, {city}\n\n' \
                                          f'<b>instagram</b>: <code>{instagram}</code>'
                        await message.answer_photo(photo=photo, caption=caption, parse_mode='html',
                                                   reply_markup=update_scores(score=smile, evaluated_id=evaluated_id))
                        not_rated += 1
                    else:
                        pass
                if not_rated == 0:
                    await message.answer('На данный момент Вы никого не оценил\n\n'
                                         'Самое время воспользоваться командой "/search" и набрать свою популярность!')
                else:
                    await message.answer('Отображаются только 20 последних пользователей')
            else:
                await message.answer('На данный момент Вы никого не оценил\n\n'
                                     'Самое время воспользоваться командой "/search" и набрать свою популярность!')


def register_handler_scores():
    dp.register_message_handler(i_was_evaluated, Text(startswith=['меня оценили', 'Меня оценили']))
    dp.register_message_handler(my_score, Text(startswith=['мои отметки', 'Мои отметки', 'Мои оценки']))
