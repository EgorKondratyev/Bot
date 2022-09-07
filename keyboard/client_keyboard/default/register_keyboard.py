from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from utilits.translate_text import translate_from_lang_russian


async def create_sex_menu(user_id: int) -> ReplyKeyboardMarkup:
    text_female = 'Я Девушка'
    text_male = 'Я парень'
    translate_female = await translate_from_lang_russian(user_id=user_id, text=text_female)
    translate_male = await translate_from_lang_russian(user_id=user_id, text=text_male)
    sex_menu = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    female_button = KeyboardButton(text=translate_female + '👧')
    male_button = KeyboardButton(text=translate_male + '👨')
    sex_menu.insert(female_button).insert(male_button)
    return sex_menu


async def create_sex_interesting_menu(user_id: int) -> ReplyKeyboardMarkup:
    text_female = await translate_from_lang_russian(user_id=user_id, text='Девушки')
    text_male = await translate_from_lang_russian(user_id=user_id, text='Парни')
    text_never_mind = await translate_from_lang_russian(user_id=user_id, text='Все равно')
    sex_interesting_menu = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    female_interesting_button = KeyboardButton(text=text_female + '👧')
    male_interesting_button = KeyboardButton(text=text_male + '👨')
    never_mind_button = KeyboardButton(text=text_never_mind + '❗️')
    sex_interesting_menu.insert(female_interesting_button).insert(male_interesting_button).insert(never_mind_button)
    return sex_interesting_menu


async def create_location_menu(user_id: int) -> ReplyKeyboardMarkup:
    location_text = await translate_from_lang_russian(user_id=user_id, text='Отправить координаты')
    location_menu = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    location_button = KeyboardButton(text=location_text + '🗺', request_location=True)
    location_menu.add(location_button)
    return location_menu


async def create_description_menu(user_id: int) -> ReplyKeyboardMarkup:
    text_skip = await translate_from_lang_russian(user_id=user_id, text='Пропустить')
    skip_description_menu = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    skip_button = KeyboardButton(text=text_skip + '😒')
    skip_description_menu.add(skip_button)
    return skip_description_menu
