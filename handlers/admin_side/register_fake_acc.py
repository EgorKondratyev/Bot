from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from geopy.geocoders import Nominatim
from fake_useragent import UserAgent

from create_bot.bot import bot, dp
from create_bot.config import admins
from databases.client_side import RegisterUserDB
from keyboard.client_keyboard.default.register_keyboard import create_sex_menu, create_sex_interesting_menu,\
    create_location_menu
from keyboard.client_keyboard.default.main_keyboard import create_main_keyboard
from states.client_states.register_states import FakeRegisterFSM
from log.log import logger


# @dp.message_handler(commands='add_fake_acc')
async def register_fake_acc(message: Message):
    if message.chat.type == 'private' and message.from_user.id in admins:
        await FakeRegisterFSM.user_id.set()
        await bot.send_message(message.from_user.id, 'Добро пожаловать в чат бота для знакомств!\n\n'
                                                     'Вы начали фейковую регистрацию аккаунта\n\n'
                                                     'Для остановки регистрации воспользуйтесь командой "/stop"')
        await message.answer('Отправьте мне телеграм ID пользователя\n\n'
                             'Пример: 54361257')


# @dp.message_handler(state=FakeRegisterFSM.user_id)
async def get_user_id(message: Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            data['user_id'] = message.text
        logger.debug('ID успешно установлен на фейковый аккаунт')

        await bot.send_message(message.from_user.id, 'Сколько тебе лет?')
        await FakeRegisterFSM.age.set()
    else:
        await message.answer('ID может быть только числовым')


# @dp.message_handler(state=FakeRegisterFSM.age)
async def get_age(message: Message, state: FSMContext):
    try:
        if message.text.isdigit():
            age = int(message.text)
            if age <= 125:

                async with state.proxy() as data:
                    data['age'] = age
                logger.debug('Возраст успешно установлен на фейковый аккаунт')

                await FakeRegisterFSM.user_sex.set()
                await message.answer('Теперь определимся с полом',
                                     reply_markup=await create_sex_menu(message.from_user.id))
            else:
                if age > 125:
                    await message.answer(f'На данный момент до {age} лет никто не доживал!\n\n'
                                         f'Необходимо указать реальный возраст (допустимое значение до 125 лет)')
                if age < 0:
                    await message.answer(f'Не существует человека в возрасте {age}\n\n'
                                         f'Необходимо указывать положительные числа!')
        else:
            await message.answer(f'Необходимо указывать возраст только в числах')
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении возраста человеку при регистрации (fake)\n\n'
                       f'{ex}')
        await message.answer('Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n'
                             'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3')
        await state.finish()


# @dp.message_handler(state=FakeRegisterFSM.user_sex)
async def get_user_sex(message: Message, state: FSMContext):
    try:
        if message.text.lower() == 'я девушка' or message.text.lower() == 'я девушка👧':
            async with state.proxy() as data:

                data['user_sex'] = 'я девушка'
            logger.debug('Пол успешно установлен на фейковый аккаунт')

            await FakeRegisterFSM.interesting_sex.set()
            await message.answer('Кто Вам интересен?',
                                 reply_markup=await create_sex_interesting_menu(message.from_user.id))

        elif message.text.lower() == 'я парень' or message.text.lower() == 'я парень👨':
            async with state.proxy() as data:

                data['user_sex'] = 'я парень'
            logger.debug('Пол успешно установлен на фейковый аккаунт')

            await FakeRegisterFSM.interesting_sex.set()
            await message.answer('Кто Вам интересен?',
                                 reply_markup=await create_sex_interesting_menu(message.from_user.id))

        else:
            await message.answer('Для того, чтобы определиться с полом необходимо нажать на одну из предложенных '
                                 'кнопок или же написать "Я девушка"/"Я парень"')
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении описания профиля человека при регистрации (fake)\n\n'
                       f'{ex}')
        await message.answer('Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n'
                             'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3\n\n'
                             'Вы можете также воспользоваться заново командой "/start"')
        await state.finish()


# @dp.message_handler(state=FakeRegisterFSM.interesting_sex)
async def get_interesting_sex(message: Message, state: FSMContext):
    try:
        # Данный участок кода можно сократить в 3 раза, однако для большей эластичности кода в последующем лучше
        # этого не делать
        if message.text.lower() == 'парни' or message.text.lower() == 'парни👨':

            async with state.proxy() as data:
                data['interesting_sex'] = 'парни'
            logger.debug('Интересующий пол успешно установлен на фейковый аккаунт')

            await FakeRegisterFSM.city.set()
            await message.answer('Из какого Вы города?', reply_markup=await create_location_menu(message.from_user.id))

        elif message.text.lower() == 'девушки' or message.text.lower() == 'девушки👧':
            async with state.proxy() as data:
                data['interesting_sex'] = 'девушки'
            logger.debug('Интересующий пол успешно установлен на фейковый аккаунт')

            await FakeRegisterFSM.city.set()
            await message.answer('Из какого Вы города?', reply_markup=await create_location_menu(message.from_user.id))

        elif message.text.lower() == 'все равно':
            async with state.proxy() as data:
                data['interesting_sex'] = 'все равно'
            logger.debug('Интересующий пол успешно установлен на фейковый аккаунт')

            await FakeRegisterFSM.city.set()
            await message.answer('Из какого Вы города?', reply_markup=await create_location_menu(message.from_user.id))
        else:
            await message.answer('Для того, чтобы определиться с тем, кто Вам интересен необходимо нажать на кнопку '
                                 'или же написать "Парни"/"Девушки"/"Все равно"')
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении описания профиля человека (fake) при регистрации\n\n'
                       f'{ex}')
        await message.answer('Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n'
                             'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3\n\n'
                             'Вы можете также воспользоваться заново командой "/start"')
        await state.finish()


# @dp.message_handler(state=FakeRegisterFSM.city)
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
                logger.debug('Город успешно установлен на фейковый аккаунт')

                await FakeRegisterFSM.name_user.set()
                await message.answer('Как мне Вас называть?', reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer('По каким-то причинам мы не смогли найти Ваш город по координатам\n\n'
                                     'Напишите вручную Ваш город или же попытайтесь отправить ещё раз')
        else:
            location = geolocator.geocode(f'{message.text}')
            if location is not None:

                async with state.proxy() as data:
                    data['location'] = str(location).split(',')[0]
                logger.debug('Город успешно установлен на фейковый аккаунт')

                await FakeRegisterFSM.name_user.set()
                await message.answer('Как мне Вас называть?', reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer(f'Мы не смогли найти город {message.text}\n\n'
                                     f'Убедитесь, что город написан без ошибок')
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении геопозиции человека (fake) при регистрации\n\n'
                       f'{ex}')
        await message.answer('Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n'
                             'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3\n\n'
                             'Вы можете также воспользоваться заново командой "/start"')
        await state.finish()


# @dp.message_handler(state=RegisterFSM.name_user)
async def get_name_user(message: Message, state: FSMContext):
    try:
        if 2 < message.text.__len__() < 45:

            async with state.proxy() as data:
                data['name'] = message.text
            logger.debug('Имя пользователя успешно установлено')

            await FakeRegisterFSM.description_user.set()
            await message.answer('Расскажите немного о себе')
        elif message.text.__len__() > 45:
            await message.answer('Имя не может превышать более 45 символов\n\n'
                                 'Если Ваше имя содержит более 45 символов, то напишите его короткую версию')
        else:
            await message.answer('Имя не может быть менее 2-ух символов')
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении имени человека при регистрации\n\n'
                       f'{ex}')
        await message.answer('Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n'
                             'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3\n\n'
                             'Вы можете также воспользоваться заново командой "/start"')
        await state.finish()


# @dp.message_handler(state=RegisterFSM.description_user)
async def get_description_user(message: Message, state: FSMContext):
    try:
        if message.text.__len__() < 1000:
            async with state.proxy() as data:
                data['description'] = message.text
            logger.debug('Описание пользователя успешно установлено')
            await FakeRegisterFSM.photo.set()
            await message.answer('Отлично! Последний шаг\n'
                                 'Отправь мне свое фото')
        else:
            await message.answer('Описание не может превышать более 1000 символов')
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении описания профиля человека при регистрации\n\n'
                       f'{ex}')
        await message.answer('Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n'
                             'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3\n\n'
                             'Вы можете также воспользоваться заново командой "/start"')
        await state.finish()


# @dp.message_handler(state=RegisterFSM.photo, content_types='any')
async def finish_register(message: Message, state: FSMContext):
    try:
        if message.photo:
            register_db = RegisterUserDB()

            photo_id = message.photo[-1].file_id
            async with state.proxy() as data:
                user_id = data['user_id']
                age = data['age']
                user_sex = data['user_sex']
                interesting_sex = data['interesting_sex']
                location = data['location']
                name_user = data['name']
                description_user = data['description']

            if not register_db.user_exists(user_id):
                register_db.user_add(user_id=user_id, age=age, user_sex=user_sex,
                                     interesting_sex=interesting_sex, city=location, name_user=name_user,
                                     description_user=description_user, photo=photo_id)
                await message.answer('Наши поздравления!\n\n'
                                     'Регистрация была успешно пройдена')
                await message.answer('Вот так выглядит Ваш профиль: ')
                caption = f'{name_user}, {age}, {location}\n\n' \
                          f'{description_user}'
                await message.answer_photo(photo=photo_id, caption=caption,
                                           reply_markup=await create_main_keyboard(message.from_user.id))
            else:
                register_db.user_update(user_id=user_id, age=age, user_sex=user_sex,
                                        interesting_sex=interesting_sex, city=location, name_user=name_user,
                                        description_user=description_user, photo=photo_id)
                await message.answer('Все данные профиля успешно обновлены')
                await message.answer('Вот так выглядит Ваш профиль: ')
                caption = f'{name_user}, {age}, {location}\n\n' \
                          f'{description_user}'
                await message.answer_photo(photo=photo_id, caption=caption,
                                           reply_markup=await create_main_keyboard(message.from_user.id))

            await state.finish()
        else:
            await message.answer('Необходимо отправить фотографию')
    except Exception as ex:
        logger.warning(f'Возникла ошибка при установлении описания профиля человека при регистрации (fake)\n\n'
                       f'{ex}')
        await message.answer('Возникла неизвестная ошибка. Просьба обратиться к администрации\n\n'
                             'Приносим прощения за доставленные неудобства. В скором времени мы все исправим >3\n\n'
                             'Вы можете также воспользоваться заново командой "/start"')
        await state.finish()


def registration_handlers_fake_register():
    dp.register_message_handler(register_fake_acc, commands='add_fake_acc')
    dp.register_message_handler(get_user_id, state=FakeRegisterFSM.user_id)
    dp.register_message_handler(get_age, state=FakeRegisterFSM.age)
    dp.register_message_handler(get_user_sex, state=FakeRegisterFSM.user_sex)
    dp.register_message_handler(get_interesting_sex, state=FakeRegisterFSM.interesting_sex)
    dp.register_message_handler(get_city, state=FakeRegisterFSM.city, content_types='any')
    dp.register_message_handler(get_name_user, state=FakeRegisterFSM.name_user)
    dp.register_message_handler(get_description_user, state=FakeRegisterFSM.description_user)
    dp.register_message_handler(finish_register, state=FakeRegisterFSM.photo, content_types='any')
