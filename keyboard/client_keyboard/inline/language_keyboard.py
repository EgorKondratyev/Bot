from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


language_menu = InlineKeyboardMarkup(row_width=3)
english_button = InlineKeyboardButton(text='English🇬🇧', callback_data='language_en')
russian_button = InlineKeyboardButton(text='Russian🇷🇺', callback_data='language_ru')
ukrainian_button = InlineKeyboardButton(text='Ukrainian🇺🇦', callback_data='language_uk')
arabic_button = InlineKeyboardButton(text='Arabic🇦🇪', callback_data='language_ar')
belarusian_button = InlineKeyboardButton(text='Belarusian🇧🇾', callback_data='language_be')
german_button = InlineKeyboardButton(text='German🇩🇪', callback_data='language_de')
polish_button = InlineKeyboardButton(text='Polish🇵🇱', callback_data='language_pl')
italian_button = InlineKeyboardButton(text='Italian🇮🇹', callback_data='language_it')
japanese_button = InlineKeyboardButton(text='Japanese🇯🇵', callback_data='language_ja')
language_menu.insert(english_button).insert(russian_button).insert(ukrainian_button).insert(arabic_button)\
    .insert(belarusian_button).insert(german_button).insert(polish_button).insert(italian_button)\
    .insert(japanese_button)
