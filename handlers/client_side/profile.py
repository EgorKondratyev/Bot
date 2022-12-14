from datetime import datetime
import traceback

from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import BadRequest

from create_bot.bot import dp
from databases.client_side import RegisterUserDB, StatisticDB
from databases.payments import VIP
from handlers.client_side.register_user import start_register
from keyboard.client_keyboard.inline.profile_keyboard import create_profile_keyboard, create_user_sex_keyboard, \
    create_interesting_sex_keyboard
from states.client_states.profile_states import PhotoChangeFSM, DescriptionChangeFSM, NameChangeFSM, AgeChangeFSM, \
    SexChangeFSM, SexInterestingChangeFSM, BindingInstagramFSM
from log.log import logger
from utilits.check_sub_channel import check_sub_channel
from utilits.translate_text import translate_from_lang_russian
from keyboard.admin_keyboard.inline.sub_channel import create_sub_channel_keyboard


async def get_attributes_user_for_profile(register_db, user_id):
    """Получение аттрибутов: возраст, город, имя пользователя, описание пользователя, фото_id, instagram"""
    info = register_db.get_all_info_by_user_id(user_id=user_id)  # ((user_id, status, age...),)
    for attributes_user in info:
        age = attributes_user[3]
        city = attributes_user[6]
        name_user = attributes_user[7]
        description_user = attributes_user[8]
        photo = attributes_user[9]
        if photo is None:
            photo = attributes_user[10]
        instagram = attributes_user[11]
        return age, city, name_user, description_user, photo, instagram


# @dp.message_handler(commands='profile')
# @dp.message_handler(Text(equals=['profile', 'профиль']))
async def profile_user(message: Message):
    try:
        if message.chat.type == 'private':
            if await check_sub_channel(message.from_user.id):
                register_db = RegisterUserDB()
                check_register_user = register_db.user_exists(user_id=message.from_user.id)
                if check_register_user:
                    # Заново отправляем профиль пользователя
                    age, city, name_user, description_user, photo, instagram = await get_attributes_user_for_profile(
                        register_db=register_db, user_id=message.from_user.id)
                    vip_db = VIP()
                    if vip_db.exists_user(user_id=message.from_user.id):
                        caption = f'{name_user}, {age}, {city} 👑\n\n'
                    else:
                        caption = f'{name_user}, {age}, {city}\n\n'
                    if instagram is None:
                        caption += f'{description_user}'
                    else:
                        if description_user:
                            caption += f'{description_user}\n\n' \
                                      f'<b>instagram</b>: <code>{instagram}</code>'
                        else:
                            caption += f'<b>instagram</b>: <code>{instagram}</code>'

                    text_your_acc = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                      text='Вот Ваша анкета: ')
                    await message.answer(text_your_acc)
                    try:
                        await message.answer_photo(photo=photo, caption=caption,
                                                   reply_markup=await create_profile_keyboard(message.from_user.id),
                                                   parse_mode='html')
                    except BadRequest:
                        await message.answer_video(video=photo, caption=caption,
                                                   reply_markup=await create_profile_keyboard(message.from_user.id),
                                                   parse_mode='html')
                else:
                    await start_register(message.from_user.id)
            else:
                text_channel_sub = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                     text='Прежде чем воспользоваться данным ботом'
                                                                          ' стоит подписаться на каналы!')
                await message.answer(text_channel_sub,
                                     reply_markup=create_sub_channel_keyboard())
    except Exception as ex:
        traceback.print_exc()
        error_text = 'Возникла ранее неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим свои извинения, в скором времени мы все исправим!'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        logger.warning(f'Возникла ошибка при "/profile"\n\n'
                       f'{ex}')


# @dp.callback_query_handler(Text(equals='fill_again'))
async def fill_again(callback: CallbackQuery):
    """Заполнение профиля с 0"""
    if callback.message.chat.type == 'private':
        if await check_sub_channel(callback.from_user.id):
            await callback.answer()
            await start_register(callback.from_user.id)
        else:
            text_channel_sub = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                                 text='Прежде чем воспользоваться данным ботом'
                                                                      ' стоит подписаться на каналы!')
            await callback.message.answer(text_channel_sub, reply_markup=create_sub_channel_keyboard())


# @dp.callback_query_handler(Text(equals='change_photo'))
async def wait_change_photo(callback: CallbackQuery):
    """Ожидание фотографии """
    if await check_sub_channel(callback.from_user.id):
        await callback.answer()
        await PhotoChangeFSM.photo_wait.set()
        text_translate_photo = await translate_from_lang_russian(callback.from_user.id,
                                                                 text='Отправьте мне фотографию')
        await callback.message.answer(text_translate_photo)
    else:
        text_channel_sub = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                             text='Прежде чем воспользоваться данным ботом'
                                                                  ' стоит подписаться на каналы!')
        await callback.message.answer(text_channel_sub, reply_markup=create_sub_channel_keyboard())


# @dp.message_handler(state=PhotoChangeFSM.photo_wait, content_types='any')
async def process_change_photo(message: Message, state: FSMContext):
    try:
        if message.photo:
            await state.finish()
            photo_id = message.photo[-1].file_id
            register_db = RegisterUserDB()
            register_db.photo_update(user_id=message.from_user.id, photo_id=photo_id)
            text_translate_photo = await translate_from_lang_russian(message.from_user.id,
                                                                     text='Фото успешно обновлено')
            await message.answer(text_translate_photo)
            logger.debug('Фото успешно обновлено')

            # Заново отправляем профиль пользователя
            age, city, name_user, description_user, photo, instagram = await get_attributes_user_for_profile(
                register_db=register_db, user_id=message.from_user.id)
            vip_db = VIP()
            if vip_db.exists_user(user_id=message.from_user.id):
                caption = f'{name_user}, {age}, {city} 👑\n\n'
            else:
                caption = f'{name_user}, {age}, {city}\n\n'
            if instagram is None:
                caption += f'{description_user}'
            else:
                if description_user:
                    caption += f'{description_user}\n\n' \
                              f'<b>instagram</b>: <code>{instagram}</code>'
                else:
                    caption += f'<b>instagram</b>: <code>{instagram}</code>'
            text_your_acc = await translate_from_lang_russian(user_id=message.from_user.id,
                                                              text='Вот Ваша анкета: ')
            await message.answer(text_your_acc)
            try:
                await message.answer_photo(photo=photo, caption=caption,
                                           reply_markup=await create_profile_keyboard(message.from_user.id),
                                           parse_mode='html')
            except BadRequest:
                await message.answer_video(video=photo, caption=caption,
                                           reply_markup=await create_profile_keyboard(message.from_user.id),
                                           parse_mode='html')

        elif message.video:
            await state.finish()
            video = message.video.file_id
            register_db = RegisterUserDB()
            register_db.video_update(user_id=message.from_user.id, video_id=video)
            logger.debug('Видео успешно обновлено')

            # Заново отправляем профиль пользователя
            age, city, name_user, description_user, photo, instagram = await get_attributes_user_for_profile(
                register_db=register_db, user_id=message.from_user.id)
            vip_db = VIP()
            if vip_db.exists_user(user_id=message.from_user.id):
                caption = f'{name_user}, {age}, {city} 👑\n\n'
            else:
                caption = f'{name_user}, {age}, {city}\n\n'
            if instagram is None:
                caption += f'{description_user}'
            else:
                if description_user:
                    caption += f'{description_user}\n\n' \
                              f'<b>instagram</b>: <code>{instagram}</code>'
                else:
                    caption += f'<b>instagram</b>: <code>{instagram}</code>'
            text_your_acc = await translate_from_lang_russian(user_id=message.from_user.id,
                                                              text='Вот Ваша анкета: ')
            await message.answer(text_your_acc)
            try:
                await message.answer_photo(photo=photo, caption=caption,
                                           reply_markup=await create_profile_keyboard(message.from_user.id),
                                           parse_mode='html')
            except BadRequest:
                await message.answer_video(video=photo, caption=caption,
                                           reply_markup=await create_profile_keyboard(message.from_user.id),
                                           parse_mode='html')
        else:
            wait_photo_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                text='Ожидалась фотография')
            await message.answer(wait_photo_text)
    except Exception as ex:
        error_text = 'Возникла ранее неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим свои извинения, в скором времени мы все исправим!'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        logger.warning(f'Возникла ошибка при изменении фотографии профиля (анкеты) пользователя\n\n'
                       f'{ex}')


# @dp.callback_query_handler(Text(equals='change_description'))
async def wait_change_description(callback: CallbackQuery):
    """Ожидание текст описания """
    if await check_sub_channel(callback.from_user.id):
        await callback.answer()
        await DescriptionChangeFSM.description_wait.set()
        text_description = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                             text='Отправьте мне новое описание')
        await callback.message.answer(text_description)
    else:
        text_channel_sub = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                             text='Прежде чем воспользоваться данным ботом'
                                                                  ' стоит подписаться на каналы!')
        await callback.message.answer(text_channel_sub, reply_markup=create_sub_channel_keyboard())


# @dp.message_handler(state=DescriptionChangeFSM.description_wait)
async def process_change_description(message: Message, state: FSMContext):
    """Процесс изменения описания"""
    try:
        if message.text.__len__() < 1000:
            await state.finish()
            register_db = RegisterUserDB()
            register_db.description_update(description=message.text, user_id=message.from_user.id)

            # Заново отправляем профиль пользователя
            age, city, name_user, description_user, photo, instagram = await get_attributes_user_for_profile(
                register_db=register_db, user_id=message.from_user.id)
            vip_db = VIP()
            if vip_db.exists_user(user_id=message.from_user.id):
                caption = f'{name_user}, {age}, {city} 👑\n\n'
            else:
                caption = f'{name_user}, {age}, {city}\n\n'
            if instagram is None:
                caption += f'{description_user}'
            else:
                if description_user:
                    caption += f'{description_user}\n\n' \
                              f'<b>instagram</b>: <code>{instagram}</code>'
                else:
                    caption += f'<b>instagram</b>: <code>{instagram}</code>'
            text_your_acc = await translate_from_lang_russian(user_id=message.from_user.id,
                                                              text='Вот Ваша анкета: ')
            await message.answer(text_your_acc)
            try:
                await message.answer_photo(photo=photo, caption=caption,
                                           reply_markup=await create_profile_keyboard(message.from_user.id),
                                           parse_mode='html')
            except BadRequest:
                await message.answer_video(video=photo, caption=caption,
                                           reply_markup=await create_profile_keyboard(message.from_user.id),
                                           parse_mode='html')
        else:
            text_big_description = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                     text='Описание не может превышать более'
                                                                          ' 1000 символов')
            await message.answer(text_big_description)
    except Exception as ex:
        error_text = 'Возникла ранее неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим свои извинения, в скором времени мы все исправим!'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        logger.warning(f'Возникла ошибка при изменении описания профиля (анкеты) пользователя\n\n'
                       f'{ex}')


# @dp.callback_query_handler(Text(equals='change_name'))
async def wait_change_name(callback: CallbackQuery):
    """Ожидание текст описания """
    if await check_sub_channel(callback.from_user.id):
        await callback.answer()
        await NameChangeFSM.name_wait.set()
        text_name = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                      text='Отправьте мне свое имя')
        await callback.message.answer(text_name)
    else:
        text_channel_sub = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                             text='Прежде чем воспользоваться данным ботом'
                                                                  ' стоит подписаться на каналы!')
        await callback.message.answer(text_channel_sub, reply_markup=create_sub_channel_keyboard())


@dp.message_handler(state=NameChangeFSM.name_wait)
async def process_change_name(message: Message, state: FSMContext):
    try:
        if 2 < message.text.__len__() < 45:
            await state.finish()
            register_db = RegisterUserDB()
            register_db.name_update(name=message.text, user_id=message.from_user.id)

            # Заново отправляем профиль пользователя
            age, city, name_user, description_user, photo, instagram = await get_attributes_user_for_profile(
                register_db=register_db, user_id=message.from_user.id)
            vip_db = VIP()
            if vip_db.exists_user(user_id=message.from_user.id):
                caption = f'{name_user}, {age}, {city} 👑\n\n'
            else:
                caption = f'{name_user}, {age}, {city}\n\n'
            if instagram is None:
                caption += f'{description_user}'
            else:
                if description_user:
                    caption += f'{description_user}\n\n' \
                              f'<b>instagram</b>: <code>{instagram}</code>'
                else:
                    caption += f'<b>instagram</b>: <code>{instagram}</code>'
            text_your_acc = await translate_from_lang_russian(user_id=message.from_user.id,
                                                              text='Вот Ваша анкета: ')
            await message.answer(text_your_acc)
            try:
                await message.answer_photo(photo=photo, caption=caption,
                                           reply_markup=await create_profile_keyboard(message.from_user.id),
                                           parse_mode='html')
            except BadRequest:
                await message.answer_video(video=photo, caption=caption,
                                           reply_markup=await create_profile_keyboard(message.from_user.id),
                                           parse_mode='html')

        elif message.text.__len__() > 45:
            text_big_name = 'Имя не может превышать более 45 символов\n\n' \
                            'Если Ваше имя содержит более 45 символов, то напишите его короткую версию'
            translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                               text=text_big_name)
            await message.answer(translate_text)
        else:
            text_little_name = 'Имя не может быть менее 2-ух символов'
            translate_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                               text=text_little_name)
            await message.answer(translate_text)
    except Exception as ex:
        error_text = 'Возникла ранее неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим свои извинения, в скором времени мы все исправим!'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        logger.warning(f'Возникла ошибка при изменении имени профиля (анкеты) пользователя\n\n'
                       f'{ex}')


# @dp.callback_query_handler(Text(equals='change_age'))
async def wait_change_age(callback: CallbackQuery):
    """Ожидание возраста"""
    if await check_sub_channel(callback.from_user.id):
        await callback.answer()
        await AgeChangeFSM.age_wait.set()
        text_age = 'Отправьте мне свой возраст'
        translate_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                           text=text_age)
        await callback.message.answer(translate_text)
    else:
        text_channel_sub = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                             text='Прежде чем воспользоваться данным ботом'
                                                                  ' стоит подписаться на каналы!')
        await callback.message.answer(text_channel_sub, reply_markup=create_sub_channel_keyboard())


# @dp.message_handler(state=AgeChangeFSM.age_wait)
async def process_age_change(message: Message, state: FSMContext):
    try:
        if message.text.isdigit():
            age = int(message.text)
            if age <= 125:
                await state.finish()
                register_db = RegisterUserDB()
                register_db.age_update(age=age, user_id=message.from_user.id)

                # Заново отправляем профиль пользователя
                age, city, name_user, description_user, photo, instagram = await get_attributes_user_for_profile(
                    register_db=register_db, user_id=message.from_user.id)
                vip_db = VIP()
                if vip_db.exists_user(user_id=message.from_user.id):
                    caption = f'{name_user}, {age}, {city} 👑\n\n'
                else:
                    caption = f'{name_user}, {age}, {city}\n\n'
                if instagram is None:
                    caption += f'{description_user}'
                else:
                    if description_user:
                        caption += f'{description_user}\n\n' \
                                  f'<b>instagram</b>: <code>{instagram}</code>'
                    else:
                        caption += f'<b>instagram</b>: <code>{instagram}</code>'
                text_your_acc = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                  text='Вот Ваша анкета: ')
                await message.answer(text_your_acc)
                try:
                    await message.answer_photo(photo=photo, caption=caption,
                                               reply_markup=await create_profile_keyboard(message.from_user.id),
                                               parse_mode='html')
                except BadRequest:
                    await message.answer_video(video=photo, caption=caption,
                                               reply_markup=await create_profile_keyboard(message.from_user.id),
                                               parse_mode='html')
            else:
                if age > 125:
                    text_big_age = f'На данный момент до {age} лет никто не доживал!\n\n' \
                                   f'Необходимо указать реальный возраст (допустимое значение до 125 лет)'
                    text_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                       text=text_big_age)
                    await message.answer(text_translate)
                if age < 0:
                    text_little_age = f'Не существует человека в возрасте {age}\n\n' \
                                      f'Необходимо указывать положительные числа!'
                    text_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                       text=text_little_age)
                    await message.answer(text_translate)
        else:
            text_str_age = await translate_from_lang_russian(user_id=message.from_user.id,
                                                             text=f'Необходимо указывать возраст только в числах')
            await message.answer(text_str_age)
    except Exception as ex:
        error_text = 'Возникла ранее неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим свои извинения, в скором времени мы все исправим!'
        error_translate = await translate_from_lang_russian(user_id=message.from_user.id,
                                                            text=error_text)
        await message.answer(error_translate)
        logger.warning(f'Возникла ошибка при изменении возраста профиля (анкеты) пользователя\n\n'
                       f'{ex}')


# @dp.callback_query_handler(Text(equals='sex_user'))
async def wait_change_user_sex(callback: CallbackQuery):
    """Ожидание смены пола"""
    await callback.answer()
    await SexChangeFSM.sex_fsm.set()
    choice_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                    text='Выберите один из ниже предложенных вариантов')
    await callback.message.answer(choice_text, reply_markup=await create_user_sex_keyboard(callback.from_user.id))


# @dp.message_handler(state=SexChangeFSM.sex_fsm)
async def need_click_button_sex(message: Message):
    """Требования нажатие кнопки, а не написания текста (при выборе пола)"""
    error_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                   text='Необходимо выбрать один из '
                                                        'предложенных вариантов пола')
    await message.answer(error_text)


# @dp.callback_query_handler(Text(equals=['male_profile', 'female_profile']), state=SexChangeFSM.sex_fsm)
async def process_change_user_sex(callback: CallbackQuery, state: FSMContext):
    try:
        sex = 'я парень'
        if callback.data == 'female_profile':
            sex = 'я девушка'

        register_db = RegisterUserDB()
        register_db.sex_update(sex=sex, user_id=callback.from_user.id)

        yes_change_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                            text='Изменения вступили в силу')
        await callback.answer(yes_change_text)

    except Exception as ex:
        error_text = 'Возникла ранее неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим свои извинения, в скором времени мы все исправим!'
        error_translate = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                            text=error_text)
        await callback.message.answer(error_translate)
        logger.warning(f'Возникла ошибка при изменении пола профиля (анкеты) пользователя\n\n'
                       f'{ex}')
    finally:
        await state.finish()


# @dp.callback_query_handler(Text(equals='sex_interesting'))
async def wait_change_sex_interesting(callback: CallbackQuery):
    """Ожидание смены пола"""
    await callback.answer()
    await SexInterestingChangeFSM.sex_interesting_fsm.set()
    choice_text = await translate_from_lang_russian(callback.from_user.id,
                                                    text='Выберите один из ниже предложенных вариантов')
    await callback.message.answer(choice_text,
                                  reply_markup=await create_interesting_sex_keyboard(callback.from_user.id))


# @dp.message_handler(state=SexInterestingChangeFSM.sex_interesting_fsm)
async def need_click_button_interesting_sex(message: Message):
    """Требования нажатие кнопки, а не написания текста (при выборе пола)"""
    error_text = await translate_from_lang_russian(message.from_user.id,
                                                   text='Необходимо выбрать один из предложенных '
                                                        'вариантов интересующего Вас пола')
    await message.answer(error_text)


# @dp.callback_query_handler(Text(equals=['female_interesting_profile',
# 'male_interesting_profile', 'never_mind_profile']))
async def process_change_sex_interesting(callback: CallbackQuery, state: FSMContext):
    try:
        sex = 'все равно'
        if sex == 'female_interesting_profile':
            sex = 'девушки'
        elif sex == 'male_interesting_profile':
            sex = 'парни'

        register_db = RegisterUserDB()
        register_db.interesting_sex_update(interesting_sex=sex, user_id=callback.from_user.id)
        logger.debug('Интересующий пол успешно изменён')

        yes_change_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                            text='Изменения вступили в силу')
        await callback.answer(yes_change_text)

    except Exception as ex:
        error_text = 'Возникла ранее неизвестная ошибка. Просьба обратиться к администрации\n\n' \
                     'Приносим свои извинения, в скором времени мы все исправим!'
        error_translate = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                            text=error_text)
        await callback.message.answer(error_translate)
        logger.warning(f'Возникла ошибка при изменении интересующего пола профиля (анкеты) пользователя\n\n'
                       f'{ex}')
    finally:
        await state.finish()


# @dp.callback_query_handler(Text(equals='binding_instagram'))
async def wait_binding_instagram(callback: CallbackQuery):
    await callback.answer()
    await BindingInstagramFSM.binding_instagram_wait.set()
    get_instagram_text = await translate_from_lang_russian(user_id=callback.from_user.id,
                                                           text='Отправьте мне свой инстаграм. Примеры:')
    await callback.message.answer(get_instagram_text +
                                  '\n\n<code>@unknown</code>\n'
                                  '<code>https://www.instagram.com/unknown</code>', parse_mode='html')


# @dp.message_handler(state=BindingInstagramFSM.binding_instagram_wait)
async def process_binding_instagram(message: Message, state: FSMContext):
    if message.text.startswith('@') or 'https://www.instagram.com/' in message.text:
        await state.finish()
        register_db = RegisterUserDB()
        instagram = message.text
        if 'https://www.instagram.com/' in message.text:
            instagram = '<code>@' + message.text[len('https://www.instagram.com/'):] + '</code>'

        register_db.update_instagram(login_instagram=instagram, user_id=message.from_user.id)
        instagram_add_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                               text='Инстаграм успешно добавлен')
        await message.answer(instagram_add_text)

        # Заново отправляем профиль пользователя
        age, city, name_user, description_user, photo, instagram = await get_attributes_user_for_profile(
            register_db=register_db, user_id=message.from_user.id)
        vip_db = VIP()
        if vip_db.exists_user(user_id=message.from_user.id):
            caption = f'{name_user}, {age}, {city} 👑\n\n'
        else:
            caption = f'{name_user}, {age}, {city}\n\n'
        if instagram is None:
            caption += f'{description_user}'
        else:
            if description_user:
                caption += f'{description_user}\n\n' \
                          f'<b>instagram</b>: <code>{instagram}</code>'
            else:
                caption += f'<b>instagram</b>: <code>{instagram}</code>'

        text_your_acc = await translate_from_lang_russian(user_id=message.from_user.id,
                                                          text='Вот Ваша анкета: ')
        await message.answer(text_your_acc)
        try:
            await message.answer_photo(photo=photo, caption=caption,
                                       reply_markup=await create_profile_keyboard(message.from_user.id),
                                       parse_mode='html')
        except BadRequest:
            await message.answer_video(video=photo, caption=caption,
                                       reply_markup=await create_profile_keyboard(message.from_user.id),
                                       parse_mode='html')
        delete_command_inst_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                     text='Для удаления instagram'
                                                                          ' воспользуйтесь командой'
                                                                          ' "/delete_instagram"')
        await message.answer(delete_command_inst_text)
    else:
        error_instagram_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                 text='Отправьте мне свой инстаграм. Примеры:')
        await message.answer(error_instagram_text +
                             '\n\n<code>@unknown</code>\n'
                             '<code>https://www.instagram.com/unknown</code>', parse_mode='html')


# @dp.message_handler(commands='delete_instagram')
async def delete_instagram(message: Message):
    if message.chat.type == 'private':
        register_db = RegisterUserDB()
        check_register_user = register_db.user_exists(user_id=message.from_user.id)
        if check_register_user:
            register_db.delete_instagram(message.from_user.id)
            instagram_delete_text = await translate_from_lang_russian(user_id=message.from_user.id,
                                                                      text='Инстаграм успешно удален')
            await message.answer(instagram_delete_text)
        else:
            await start_register(message.from_user.id)


# @dp.callback_query_handler(Text(equals='statistic'))
async def get_statistic_user(callback: CallbackQuery):
    await callback.answer()
    statistic_db = StatisticDB()
    user_info = statistic_db.get_all_info(user_id=callback.from_user.id)  # ((info1, info2), )
    if user_info:
        attribute_info = user_info[0]

        my_scores = attribute_info[1]
        their_scores = attribute_info[2]
        residence_time = attribute_info[3]
        amount_my_complain = attribute_info[4]
        amount_their_complain = attribute_info[5]

        residence_time = datetime.utcfromtimestamp(residence_time).strftime('%Y-%m-%d %H:%M:%S')
        statistic_text = \
            await translate_from_lang_russian(user_id=callback.from_user.id,
                                              text=f'Статистика📈\n\n'
                                                   f'😍Ваши отметки: <b>{my_scores} человек</b>\n'
                                                   f'🥰Ваc оценили: <b>{their_scores} человек</b>\n\n'
                                                   f'🔐Вы пожаловались: <b>на {amount_my_complain} человек(-а)</b>\n'
                                                   f'🫥На Вас пожаловались: <b>на {amount_their_complain} человек(-а)</b> \n\n'
                                                   f'📆Вы в боте с <b>{residence_time}</b>\n\n'
                                                   f'/statistic_vip')
        await callback.message.answer(text=statistic_text, parse_mode='html')


def register_handler_profile():
    dp.register_message_handler(profile_user, commands='profile')
    dp.register_message_handler(profile_user, Text(startswith='📄'))
    dp.register_callback_query_handler(fill_again, Text(equals='fill_again'))
    dp.register_callback_query_handler(wait_change_photo, Text(equals='change_photo'), state=None)
    dp.register_message_handler(process_change_photo, state=PhotoChangeFSM.photo_wait, content_types='any')
    dp.register_callback_query_handler(wait_change_description, Text(equals='change_description'))
    dp.register_message_handler(process_change_description, state=DescriptionChangeFSM.description_wait)
    dp.register_callback_query_handler(wait_change_name, Text(equals='change_name'))
    dp.register_message_handler(process_change_name, state=NameChangeFSM.name_wait)
    dp.register_callback_query_handler(wait_change_age, Text(equals='change_age'))
    dp.register_message_handler(process_age_change, state=AgeChangeFSM.age_wait)
    dp.register_callback_query_handler(wait_change_user_sex, Text(equals='sex_user'))
    dp.register_message_handler(need_click_button_sex, state=SexChangeFSM.sex_fsm)
    dp.register_callback_query_handler(process_change_user_sex, Text(equals=['male_profile', 'female_profile']),
                                       state=SexChangeFSM.sex_fsm)
    dp.register_callback_query_handler(wait_change_sex_interesting, Text(equals='sex_interesting'))
    dp.register_message_handler(need_click_button_interesting_sex, state=SexInterestingChangeFSM.sex_interesting_fsm)
    dp.register_callback_query_handler(process_change_sex_interesting,
                                       Text(equals=['female_interesting_profile', 'male_interesting_profile',
                                                    'never_mind_profile']),
                                       state=SexInterestingChangeFSM.sex_interesting_fsm)
    dp.register_callback_query_handler(wait_binding_instagram, Text(equals='binding_instagram'))
    dp.register_message_handler(process_binding_instagram, state=BindingInstagramFSM.binding_instagram_wait)
    dp.register_message_handler(delete_instagram, commands='delete_instagram')
    dp.register_callback_query_handler(get_statistic_user, Text(equals='statistic'))
