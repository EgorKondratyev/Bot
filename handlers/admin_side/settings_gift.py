from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text

from create_bot.admin_bot import admin_dp
from create_bot.config import admins
from databases.admin_side import GiftDB
from keyboard.admin_keyboard.inline.gift_keyboard import gift_menu


# @admin_dp.message_handler(commands='settings_gift')
async def settings_gift(message: Message):
    if message.chat.type == 'private' and message.from_user.id in admins:
        gift_db = GiftDB()
        one_day = gift_db.get_gift_one_day()
        three_day = gift_db.get_gift_three_day()
        no_gift = gift_db.get_nogift()
        if one_day:
            gift_one = 'Включено'
        else:
            gift_one = 'Выключено'

        if three_day:
            gift_three = 'Включено'
        else:
            gift_three = 'Выключено'

        if no_gift:
            gift_no = 'Включено'
        else:
            gift_no = 'Выключено'
        await message.answer(f'При установке подарка один день, 3 дня или же ничего, то остальные будут отключаться\n\n'
                             f'Один день: {gift_one}\n'
                             f'Три дня: {gift_three}\n'
                             f'Без подарка: {gift_no}\n\n'
                             f'Выберите один из вариантов ниже: ', reply_markup=gift_menu)


@admin_dp.callback_query_handler(Text(startswith='gift_'))
async def change_gift(callback: CallbackQuery):
    if callback.message.chat.type == 'private' and callback.from_user.id in admins:
        await callback.answer()
        gift = callback.data[5:]
        gift_db = GiftDB()
        if gift == 'one_day':
            gift_db.set_gift(one_day=True)
        elif gift == 'three_day':
            gift_db.set_gift(three_day=True)
        else:
            gift_db.set_gift(no_gift=True)
        await callback.message.answer('Успешно')


def register_handlers_settings_gift():
    admin_dp.register_message_handler(settings_gift, commands='settings_gift')
