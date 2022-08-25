from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


profile_inline = InlineKeyboardMarkup(row_width=2)
fill_again_button = InlineKeyboardButton(text='📃Заполнить заново', callback_data='fill_again')
change_photo_button = InlineKeyboardButton(text='📷Фото/видео', callback_data='change_photo')
change_description_button = InlineKeyboardButton(text='📚Описание', callback_data='change_description')
change_name_button = InlineKeyboardButton(text='🧒Имя', callback_data='change_name')
change_age_button = InlineKeyboardButton(text='📅Возраст', callback_data='change_age')
sex_user_button = InlineKeyboardButton(text='‍👨Мой пол', callback_data='sex_user')
sex_interesting_button = InlineKeyboardButton(text='🏳️‍⚧️Выбор пола', callback_data='sex_interesting')
binding_instagram_button = InlineKeyboardButton(text='💻Привязать инстаграм', callback_data='binding_instagram')
statistic_button = InlineKeyboardButton(text='📈Статистика', callback_data='statistic')
profile_inline.insert(fill_again_button).add(change_photo_button).insert(change_description_button)\
    .insert(change_name_button).insert(change_age_button).insert(sex_user_button).insert(sex_interesting_button)\
    .insert(binding_instagram_button).add(statistic_button)


change_user_sex_inline = InlineKeyboardMarkup(row_width=2)
male_button = InlineKeyboardButton(text='Парень👨', callback_data='male_profile')
female_button = InlineKeyboardButton(text='Девушка👧', callback_data='female_profile')
change_user_sex_inline.insert(male_button).insert(female_button)


change_interesting_sex_inline = InlineKeyboardMarkup(row_width=3)
female_interesting_button = InlineKeyboardButton(text='Девушки👧', callback_data='female_interesting_profile')
male_interesting_button = InlineKeyboardButton(text='Парни👨', callback_data='male_interesting_profile')
never_mind_button = InlineKeyboardButton(text='Все равно', callback_data='never_mind_profile')
change_interesting_sex_inline.insert(female_interesting_button).insert(male_interesting_button).insert(never_mind_button)
