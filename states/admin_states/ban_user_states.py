from aiogram.dispatcher.filters.state import State, StatesGroup


class BanUserFSM(StatesGroup):
    get_id_user = State()
    confirm = State()


class UnBanUserFSM(StatesGroup):
    get_id_user = State()
    confirm = State()
