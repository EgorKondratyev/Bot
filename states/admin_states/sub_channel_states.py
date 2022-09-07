from aiogram.dispatcher.filters.state import State, StatesGroup


class SubChannelFSM(StatesGroup):
    get_channel_id = State()
    get_channel_name = State()
