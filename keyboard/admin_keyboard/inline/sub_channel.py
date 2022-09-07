from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from databases.admin_side import ChannelDB


def create_sub_channel_keyboard() -> InlineKeyboardMarkup:
    channels_id = ChannelDB().get_channels()
    sub_channel_menu = InlineKeyboardMarkup(row_width=1)
    for channel in channels_id:
        sub_channel_button = InlineKeyboardButton(text=f'Подписаться на {channel[1]}',
                                                  url=f'https://t.me/' + channel[0][1:])
        sub_channel_menu.add(sub_channel_button)
    return sub_channel_menu
