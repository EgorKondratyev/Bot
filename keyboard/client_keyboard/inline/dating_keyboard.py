from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def scores(user_id: int) -> InlineKeyboardMarkup:
    scores_menu = InlineKeyboardMarkup(row_width=5)
    score_button_1 = InlineKeyboardButton(text='1🥶', callback_data=f'score_1🥶_{user_id}')
    score_button_2 = InlineKeyboardButton(text='2🥱', callback_data=f'score_2🥱_{user_id}')
    score_button_3 = InlineKeyboardButton(text='3🙂', callback_data=f'score_3🙂_{user_id}')
    score_button_4 = InlineKeyboardButton(text='4😚', callback_data=f'score_4😚_{user_id}')
    score_button_5 = InlineKeyboardButton(text='5😍', callback_data=f'score_5😍_{user_id}')
    complain_button = InlineKeyboardButton(text='⚠Complain⚠', callback_data=f'complain_on_user_{user_id}')
    scores_menu.insert(score_button_1).insert(score_button_2).insert(score_button_3).insert(score_button_4).\
        insert(score_button_5).insert(complain_button)
    return scores_menu


def update_scores(score: str, evaluated_id: int) -> InlineKeyboardMarkup:
    update_scores_menu = InlineKeyboardMarkup(row_width=1)
    score_button = InlineKeyboardButton(text=f'Score: {score}', callback_data='finish_score')
    write_button = InlineKeyboardButton(text='To write📩', callback_data=f'write_user_{evaluated_id}')
    update_scores_menu.insert(score_button).insert(write_button)
    return update_scores_menu


complain_menu = InlineKeyboardMarkup(row_width=1)
complain_finish_button = InlineKeyboardButton(text='The complaint has been successfully sent',
                                              callback_data='finish_complain')
complain_menu.insert(complain_finish_button)

