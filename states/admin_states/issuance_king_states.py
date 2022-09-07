from aiogram.dispatcher.filters.state import State, StatesGroup


class IssuanceKingFSM(StatesGroup):
    get_id = State()
    confirm = State()
