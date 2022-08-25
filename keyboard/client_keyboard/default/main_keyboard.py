from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

see_questionnaires_button = KeyboardButton('Смотреть анкеты🚀')
my_scores_button = KeyboardButton('Мои оценки🥰')
heir_scores_button = KeyboardButton('Меня оценили😍')
top_button = KeyboardButton('Топ👑')
vip = KeyboardButton('VIP👑')

main_menu = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
profile_button = KeyboardButton(text='Профиль📄')
main_menu.insert(see_questionnaires_button).insert(my_scores_button).insert(heir_scores_button).add(profile_button)\
    .add(top_button).insert(vip)
