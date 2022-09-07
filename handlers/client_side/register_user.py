import time

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from geopy.geocoders import Nominatim
from fake_useragent import UserAgent

from create_bot.bot import bot, dp
from databases.client_side import RegisterUserDB, ScoresDB, StatisticDB, LanguageDB
from databases.payments import VIP
from databases.admin_side import GiftDB
from keyboard.client_keyboard.default.register_keyboard import create_sex_menu, create_sex_interesting_menu, \
    create_location_menu, create_description_menu
from keyboard.client_keyboard.inline.language_keyboard import language_menu
from keyboard.client_keyboard.default.main_keyboard import create_main_keyboard
from states.client_states.register_states import RegisterFSM
from log.log import logger
from utilits.translate_text import translate_from_lang_russian


async def start_register(user_id: int):
    await bot.send_message(user_id, 'Welcome to the chat bot for dating!\n\n'
                                    'To get started, you will have to go through a simple registration!')
    await bot.send_message(user_id, 'Choose one of the languages you want to use for this bot: ',
                           reply_markup=language_menu)
    await RegisterFSM.language.set()


@dp.callback_query_handler(Text(startswith='language_'), state=RegisterFSM.language)
async def choice_language(callback: CallbackQuery, state: FSMContext):
    try:
        language_db = LanguageDB()
        if not language_db.exists_user(user_id=callback.from_user.id):
            language_db.add_user(user_id=callback.from_user.id, language=callback.data[len('language_'):])
        else:
            language_db.update_user(user_id=callback.from_user.id, language=callback.data[len('language_'):])
        await callback.answer()
        text_age_translate = await translate_from_lang_russian(user_id=callback.from_user.id, text='Сколько Вам лет?')
        await bot.send_message(callback.from_user.id, text_age_translate)
        await RegisterFSM.age.set()
    except Exception as ex:
        pass


# @dp.message_handler(state=RegisterFSM.age)
async def get_age(message: Message, state: FSMContext):
    try:
        if message.text.isdigit():
            age = int(message.text)
            if age <= 125:

                async with state.proxy() as data:
                    data['age'] = age
                logger.debug('Возраст успешно установлен')

                await RegisterFSM.user_sex.set()
                sex_age_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                      text='Теперь определимся с полом')
                await message.answer(sex_age_translate,
                                     reply_markup=await create_sex_menu(message.from_user.id))
            else:
                if age > 125:
                    text_many_age = f'На данный момент до {age} лет никто не доживал!\n\n' \
                                    f'Необходимо указать реальный возраст (допустимое значение до 125 лет)'
                    translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                       text=text_many_age)
                    await message.answer(translate_text)
                if age < 0:
                    text_little_age = f'Не существует человека в возрасте {age}\n\n' \
                                      f'Необходимо указывать положительные числа!'
                    translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                       text=text_little_age)
                    await message.answer(translate_text)
        else:
            text_age_str = f'Необходимо указывать возраст только в числах'
            translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                               text=text_age_str)
            await message.answer(translate_text)
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении возраста человеку при регистрации\n\n'
                       f'{ex}')
        error_text = 'Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        await state.finish()


# @dp.message_handler(state=RegisterFSM.user_sex)
async def get_user_sex(message: Message, state: FSMContext):
    try:
        if message.text.lower() == 'я девушка' or message.text.lower() == 'я девушка👧' or '👧' in \
                message.text.lower():
            async with state.proxy() as data:

                data['user_sex'] = 'я девушка'
            logger.debug('Пол успешно установлен')

            await RegisterFSM.interesting_sex.set()
            text_interesting_sex = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                     text='Кто Вам интересен?')
            await message.answer(text_interesting_sex,
                                 reply_markup=await create_sex_interesting_menu(message.from_user.id))

        elif message.text.lower() == 'я парень' or message.text.lower() == 'я парень👨' or '👨' in message.text.lower():
            async with state.proxy() as data:

                data['user_sex'] = 'я парень'
            logger.debug('Пол успешно установлен')

            await RegisterFSM.interesting_sex.set()
            text_interesting_sex = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                     text='Кто Вам интересен?')
            await message.answer(text_interesting_sex,
                                 reply_markup=await create_sex_interesting_menu(message.from_user.id))

        else:
            text_decide = 'Для того, чтобы определиться с полом необходимо нажать на одну из предложенных ' \
                          'кнопок или же написать "Я девушка"/"Я парень"'
            text_decide_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                      text=text_decide)
            await message.answer(text_decide_translate)
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении описания профиля человека при регистрации\n\n'
                       f'{ex}')
        error_text = 'Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3' \
                     'Вы можете также воспользоваться заново командой "/start"'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        await state.finish()


# @dp.message_handler(state=RegisterFSM.interesting_sex)
async def get_interesting_sex(message: Message, state: FSMContext):
    try:
        # Данный участок кода можно сократить в 3 раза, однако для большей эластичности кода в последующем лучше
        # этого не делать
        if message.text.lower() == 'парни' or message.text.lower() == 'парни👨' or '👨' in message.text.lower():

            async with state.proxy() as data:
                data['interesting_sex'] = 'парни'
            logger.debug('Интересующий пол успешно установлен')

            await RegisterFSM.city.set()
            city_translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                    text='Из какого Вы города?')
            await message.answer(city_translate_text, reply_markup=await create_location_menu(message.from_user.id))

        elif message.text.lower() == 'девушки' or message.text.lower() == 'девушки👧' or '👧' in message.text.lower():
            async with state.proxy() as data:
                data['interesting_sex'] = 'девушки'
            logger.debug('Интересующий пол успешно установлен')

            await RegisterFSM.city.set()
            city_translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                    text='Из какого Вы города?')
            await message.answer(city_translate_text, reply_markup=await create_location_menu(message.from_user.id))

        elif message.text.lower() == 'все равно' or '❗️' in message.text.lower():
            async with state.proxy() as data:
                data['interesting_sex'] = 'все равно'
            logger.debug('Интересующий пол успешно установлен')

            await RegisterFSM.city.set()
            city_translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                    text='Из какого Вы города?')
            await message.answer(city_translate_text, reply_markup=await create_location_menu(message.from_user.id))
        else:
            decide_text = 'Для того, чтобы определиться с тем, кто Вам интересен необходимо нажать на одну ' \
                          'из предоставленных кнопок'
            translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                               text=decide_text)
            await message.answer(translate_text)
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении описания профиля человека при регистрации\n\n'
                       f'{ex}')
        error_text = 'Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3' \
                     'Вы можете также воспользоваться заново командой "/start"'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        await state.finish()


# @dp.message_handler(state=RegisterFSM.city)
async def get_city(message: Message, state: FSMContext):
    user_agent = UserAgent().opera
    geolocator = Nominatim(user_agent=user_agent)
    try:
        if message.location:
            latitude = message.location.latitude
            longitude = message.location.longitude
            location = geolocator.geocode(f'{latitude}, {longitude}')
            if location is not None:

                async with state.proxy() as data:
                    data['location'] = str(location).split(',')[0]
                logger.debug('Город успешно установлен')

                await RegisterFSM.name_user.set()
                name_translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                        text='Как мне Вас называть?')
                await message.answer(name_translate_text, reply_markup=ReplyKeyboardRemove())
            else:
                unknown_city_text = 'По каким-то причинам мы не смогли найти Ваш город по координатам\n\n' \
                                    'Напишите вручную Ваш город или же попытайтесь отправить ещё раз'
                translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                   text=unknown_city_text)
                await message.answer(translate_text)
        else:
            location = geolocator.geocode(f'{message.text}')
            if location is not None:

                async with state.proxy() as data:
                    data['location'] = str(location).split(',')[0]
                logger.debug('Город успешно установлен')

                await RegisterFSM.name_user.set()
                name_translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                        text='Как мне Вас называть?')
                await message.answer(name_translate_text, reply_markup=ReplyKeyboardRemove())
            else:
                unknown_city_text = 'Мы не смогли найти город {message.text}\n\n' \
                                    'Убедитесь, что город написан без ошибок'
                translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                   text=unknown_city_text)
                await message.answer(translate_text)
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении геопозиции человека при регистрации\n\n'
                       f'{ex}')
        error_text = 'Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3' \
                     'Вы можете также воспользоваться заново командой "/start"'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        await state.finish()


# @dp.message_handler(state=RegisterFSM.name_user)
async def get_name_user(message: Message, state: FSMContext):
    try:
        if 2 < message.text.__len__() < 45:

            async with state.proxy() as data:
                data['name'] = message.text
            logger.debug('Имя пользователя успешно установлено')

            await RegisterFSM.description_user.set()
            description_translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                           text='Расскажите немного о себе')
            await message.answer(description_translate_text,
                                 reply_markup=await create_description_menu(message.from_user.id))
        elif message.text.__len__() > 45:
            name_big_text = 'Имя не может превышать более 45 символов\n\n' \
                            'Если Ваше имя содержит более 45 символов, то напишите его короткую версию'
            translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                               text=name_big_text)
            await message.answer(translate_text)
        else:
            name_little_text = 'Имя не может быть менее 2-ух символов'
            translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                               text=name_little_text)
            await message.answer(translate_text)
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении имени человека при регистрации\n\n'
                       f'{ex}')
        error_text = 'Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3' \
                     'Вы можете также воспользоваться заново командой "/start"'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        await state.finish()


# @dp.message_handler(state=RegisterFSM.description_user)
async def get_description_user(message: Message, state: FSMContext):
    try:
        if message.text.__len__() < 1000:
            async with state.proxy() as data:
                if message.text != 'Пропустить' or '😒' not in message.text:
                    data['description'] = message.text
                else:
                    data['description'] = ''
            logger.debug('Описание пользователя успешно установлено')
            await RegisterFSM.photo.set()
            photo_translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                     text='Отлично! Последний шаг\n'
                                                                          'Отправь мне свое фото')
            await message.answer(photo_translate_text, reply_markup=ReplyKeyboardRemove())
        else:
            text_big_description =\
                await translate_from_lang_russian(user_id=message.from_user.id,
                                                  text='Описание не может превышать более 1000 символов')
            await message.answer(text_big_description)
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении описания профиля человека при регистрации\n\n'
                       f'{ex}')
        error_text = 'Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3' \
                     'Вы можете также воспользоваться заново командой "/start"'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        await state.finish()


# @dp.message_handler(state=RegisterFSM.photo, content_types='any')
async def finish_register(message: Message, state: FSMContext):
    try:
        if message.photo:
            register_db = RegisterUserDB()

            photo_id = message.photo[-1].file_id
            async with state.proxy() as data:
                age = data['age']
                user_sex = data['user_sex']
                interesting_sex = data['interesting_sex']
                location = data['location']
                name_user = data['name']
                description_user = data['description']

            if not register_db.user_exists(message.from_user.id):
                score_db = ScoresDB()
                statistic_db = StatisticDB()
                score_db.user_add(user_id=message.from_user.id)
                statistic_db.user_add(user_id=message.from_user.id, residence_time=int(time.time()))

                register_db.user_add(user_id=message.from_user.id, age=age, user_sex=user_sex,
                                     interesting_sex=interesting_sex, city=location, name_user=name_user,
                                     description_user=description_user, photo=photo_id)
                register_db.add_evaluated(user_id=message.from_user.id, evaluated_id=message.from_user.id)
                congratulations_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                         text='Наши поздравления!\n\n'
                                                                              'Регистрация была успешно пройдена')
                await message.answer(congratulations_text)
                profile_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                 text='Вот так выглядит Ваш профиль: ')
                await message.answer(profile_text)
                caption = f'{name_user}, {age}, {location}\n\n' \
                          f'{description_user}'
                await message.answer_photo(photo=photo_id, caption=caption,
                                           reply_markup=await create_main_keyboard(message.from_user.id))
                gift_db = GiftDB()
                one_day = gift_db.get_gift_one_day()
                three_day = gift_db.get_gift_three_day()
                if one_day:
                    gift_vip_text = 'В честь первой регистрации мы предоставляем Вам VIP на 1 день!'
                    translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                       text=gift_vip_text)
                    await message.answer(translate_text)
                    # Выдача VIP в знак регистрации на 3 дня
                    vip_db = VIP()
                    vip_db.update_status_vip(user_id=message.from_user.id, status_vip=True, time_vip=86400)
                elif three_day:
                    gift_vip_text = 'В честь первой регистрации мы предоставляем Вам VIP на 3 дня!'
                    translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                       text=gift_vip_text)
                    await message.answer(translate_text)
                    # Выдача VIP в знак регистрации на 3 дня
                    vip_db = VIP()
                    vip_db.update_status_vip(user_id=message.from_user.id, status_vip=True, time_vip=259200)
                else:
                    pass
            else:
                register_db.user_update(user_id=message.from_user.id, age=age, user_sex=user_sex,
                                        interesting_sex=interesting_sex, city=location, name_user=name_user,
                                        description_user=description_user, photo=photo_id)
                congratulations_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                         text='Все данные профиля успешно обновлены')
                await message.answer(congratulations_text)
                profile_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                 text='Вот так выглядит Ваш профиль: ')
                await message.answer(profile_text)
                caption = f'{name_user}, {age}, {location}\n\n' \
                          f'{description_user}'
                await message.answer_photo(photo=photo_id, caption=caption,
                                           reply_markup=await create_main_keyboard(message.from_user.id))

            await state.finish()

        elif message.video:
            vip_db = VIP()
            if vip_db.exists_user(user_id=message.from_user.id):
                register_db = RegisterUserDB()

                video_id = message.video.file_id
                async with state.proxy() as data:
                    age = data['age']
                    user_sex = data['user_sex']
                    interesting_sex = data['interesting_sex']
                    location = data['location']
                    name_user = data['name']
                    description_user = data['description']

                if not register_db.user_exists(message.from_user.id):
                    score_db = ScoresDB()
                    statistic_db = StatisticDB()
                    score_db.user_add(user_id=message.from_user.id)
                    statistic_db.user_add(user_id=message.from_user.id, residence_time=int(time.time()))

                    register_db.user_add(user_id=message.from_user.id, age=age, user_sex=user_sex,
                                         interesting_sex=interesting_sex, city=location, name_user=name_user,
                                         description_user=description_user, video=video_id)
                    register_db.add_evaluated(user_id=message.from_user.id, evaluated_id=message.from_user.id)
                    congratulations_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                             text='Наши поздравления!\n\n'
                                                                                  'Регистрация была успешно пройдена')
                    await message.answer(congratulations_text)
                    profile_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                     text='Вот так выглядит Ваш профиль: ')
                    await message.answer(profile_text)
                    caption = f'{name_user}, {age}, {location}\n\n' \
                              f'{description_user}'
                    await message.answer_video(video=video_id, caption=caption,
                                               reply_markup=await create_main_keyboard(message.from_user.id))
                else:
                    register_db.user_update(user_id=message.from_user.id, age=age, user_sex=user_sex,
                                            interesting_sex=interesting_sex, city=location, name_user=name_user,
                                            description_user=description_user, video=video_id)
                    congratulations_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                             text='Все данные профиля успешно обновлены')
                    await message.answer(congratulations_text)
                    profile_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                     text='Вот так выглядит Ваш профиль: ')
                    await message.answer(profile_text)
                    caption = f'{name_user}, {age}, {location}\n\n' \
                              f'{description_user}'
                    await message.answer_video(video=video_id, caption=caption,
                                               reply_markup=await create_main_keyboard(message.from_user.id))

                await state.finish()
            else:
                required_vip_text = 'Чтобы загружать видео необходимо приобрести VIP статус!\n\n' \
                                    '"/vip" - приобрести VIP статус'
                translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                   text=required_vip_text)
                await message.answer(translate_text)
        else:
            required_media_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                    text='Необходимо отправить фото/видео')
            await message.answer(required_media_text)
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении описания профиля человека при регистрации\n\n'
                       f'{ex}')
        error_text = 'Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3' \
                     'Вы можете также воспользоваться заново командой "/start"'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        await state.finish()


def registration_of_registration_handlers():
    # Nice name func >3
    dp.register_message_handler(get_age, state=RegisterFSM.age)
    dp.register_message_handler(get_user_sex, state=RegisterFSM.user_sex)
    dp.register_message_handler(get_interesting_sex, state=RegisterFSM.interesting_sex)
    dp.register_message_handler(get_city, state=RegisterFSM.city, content_types='any')
    dp.register_message_handler(get_name_user, state=RegisterFSM.name_user)
    dp.register_message_handler(get_description_user, state=RegisterFSM.description_user)
    dp.register_message_handler(finish_register, state=RegisterFSM.photo, content_types='any')
