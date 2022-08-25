from create_bot.bot import bot


async def check_sub_channel(user_id: int, channel_id: str) -> bool:
    chat_member = await bot.get_chat_member(user_id=user_id, chat_id=channel_id)
    if chat_member['status'] != 'left':
        return True
    return False
