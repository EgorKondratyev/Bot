from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from databases.client_side import LanguageDB
from utilits.translate_text import translate_from_lang_russian


async def create_profile_keyboard(user_id: int) -> InlineKeyboardMarkup:
    language_db = LanguageDB()
    language = language_db.get_language_user(user_id)
    if language == 'en':
        fill_again_text = 'Fill in again'
        change_photo_text = 'Photo/video'
        change_description_text = 'Description'
        change_name_text = 'Name'
        change_age_text = 'Age'
        sex_user_sex = 'My sex'
        sex_interesting_text = 'Gender selection'
        binding_instagram_text = 'Binding instagram'
        statistic_texts = 'Statistic'
    else:
        fill_again_text = await translate_from_lang_russian(user_id=user_id, text='Заполнить заново')
        change_photo_text = await translate_from_lang_russian(user_id=user_id, text='Фото/видео')
        change_description_text = await translate_from_lang_russian(user_id=user_id, text='Описание')
        change_name_text = await translate_from_lang_russian(user_id=user_id, text='Имя')
        change_age_text = await translate_from_lang_russian(user_id=user_id, text='Возраст')
        sex_user_sex = await translate_from_lang_russian(user_id=user_id, text='Мой пол')
        sex_interesting_text = await translate_from_lang_russian(user_id=user_id, text='Выбор пола')
        binding_instagram_text = await translate_from_lang_russian(user_id=user_id, text='Привязать инстаграм')
        statistic_texts = await translate_from_lang_russian(user_id=user_id, text='Статистика')
    profile_inline = InlineKeyboardMarkup(row_width=2)
    fill_again_button = InlineKeyboardButton(text='📃' + fill_again_text, callback_data='fill_again')
    change_photo_button = InlineKeyboardButton(text='📷' + change_photo_text, callback_data='change_photo')
    change_description_button = InlineKeyboardButton(text='📚' + change_description_text,
                                                     callback_data='change_description')
    change_name_button = InlineKeyboardButton(text='🧒' + change_name_text, callback_data='change_name')
    change_age_button = InlineKeyboardButton(text='📅' + change_age_text, callback_data='change_age')
    sex_user_button = InlineKeyboardButton(text='‍👨' + sex_user_sex, callback_data='sex_user')
    sex_interesting_button = InlineKeyboardButton(text='🏳️‍⚧️' + sex_interesting_text, callback_data='sex_interesting')
    binding_instagram_button = InlineKeyboardButton(text='💻' + binding_instagram_text,
                                                    callback_data='binding_instagram')
    statistic_button = InlineKeyboardButton(text='📈' + statistic_texts, callback_data='statistic')
    profile_inline.insert(fill_again_button).add(change_photo_button).insert(change_description_button)\
        .insert(change_name_button).insert(change_age_button).insert(sex_user_button).insert(sex_interesting_button)\
        .insert(binding_instagram_button).add(statistic_button)
    return profile_inline


async def create_user_sex_keyboard(user_id: int) -> InlineKeyboardMarkup:
    male_text = await translate_from_lang_russian(user_id=user_id, text='Парень')
    female_text = await translate_from_lang_russian(user_id=user_id, text='Девушка')
    change_user_sex_inline = InlineKeyboardMarkup(row_width=2)
    male_button = InlineKeyboardButton(text=male_text + '👨', callback_data='male_profile')
    female_button = InlineKeyboardButton(text=female_text + '👧', callback_data='female_profile')
    change_user_sex_inline.insert(male_button).insert(female_button)
    return change_user_sex_inline


async def create_interesting_sex_keyboard(user_id: int) -> InlineKeyboardMarkup:
    male_text = await translate_from_lang_russian(user_id=user_id, text='Парни')
    female_text = await translate_from_lang_russian(user_id=user_id, text='Девушки')
    never_mind_text = await translate_from_lang_russian(user_id=user_id, text='Все равно')
    change_interesting_sex_inline = InlineKeyboardMarkup(row_width=3)
    female_interesting_button = InlineKeyboardButton(text=female_text + '👧', callback_data='female_interesting_profile')
    male_interesting_button = InlineKeyboardButton(text=male_text + '👨', callback_data='male_interesting_profile')
    never_mind_button = InlineKeyboardButton(text=never_mind_text, callback_data='never_mind_profile')
    change_interesting_sex_inline.insert(female_interesting_button).insert(male_interesting_button)\
        .insert(never_mind_button)
    return change_interesting_sex_inline
