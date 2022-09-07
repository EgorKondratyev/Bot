from create_bot.bot import bot
from databases.admin_side import ChannelDB


async def check_sub_channel(user_id: int) -> bool:
    channels_id = ChannelDB().get_channels()
    for channel_id in channels_id:
        try:
            chat_member = await bot.get_chat_member(user_id=user_id, chat_id=channel_id[0])
        except Exception:
            pass
        if chat_member['status'] != 'left':
            pass
        else:
            return False
    return True
