from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


from databases.client_side import LanguageDB
from utilits.translate_text import translate_from_lang_russian


async def create_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    language_db = LanguageDB()
    language = language_db.get_language_user(user_id=user_id)
    if language == 'en':
        see_questionnaires_text = 'View questionnaires'
        my_scores_text = 'My grades'
        heir_scores_text = 'I was appreciated'
        profile_text = 'Profile'
    else:
        see_questionnaires_text = await translate_from_lang_russian(user_id=user_id, text='Смотреть анкеты')
        my_scores_text = await translate_from_lang_russian(user_id=user_id, text='Мои оценки')
        heir_scores_text = await translate_from_lang_russian(user_id=user_id, text='Меня оценили')
        profile_text = await translate_from_lang_russian(user_id=user_id, text='Профиль')
    see_questionnaires_button = KeyboardButton('🚀' + see_questionnaires_text)
    my_scores_button = KeyboardButton('🥰' + my_scores_text)
    heir_scores_button = KeyboardButton('😍' + heir_scores_text)
    top_button = KeyboardButton('TOP👑')
    vip = KeyboardButton('VIP👑')

    main_menu = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    profile_button = KeyboardButton(text='📄' + profile_text)
    main_menu.insert(see_questionnaires_button).insert(my_scores_button).insert(heir_scores_button).add(profile_button)\
        .add(top_button).insert(vip)
    return main_menu
