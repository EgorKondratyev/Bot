from aiogram.dispatcher.filters.state import State, StatesGroup


class IssuanceVIPFSM(StatesGroup):
    get_id = State()
    day_time = State()
