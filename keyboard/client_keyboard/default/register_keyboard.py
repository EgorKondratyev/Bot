from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


sex_menu = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
female_button = KeyboardButton(text='Я Девушка👧')
male_button = KeyboardButton(text='Я парень👨')
sex_menu.insert(female_button).insert(male_button)

sex_interesting_menu = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
female_interesting_button = KeyboardButton(text='Девушки👧')
male_interesting_button = KeyboardButton(text='Парни👨')
never_mind_button = KeyboardButton(text='Все равно')
sex_interesting_menu.insert(female_interesting_button).insert(male_interesting_button).insert(never_mind_button)

location_menu = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
location_button = KeyboardButton(text='Отправить координаты🗺', request_location=True)
location_menu.add(location_button)

skip_description_menu = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
skip_button = KeyboardButton(text='Пропустить')
skip_description_menu.add(skip_button)
