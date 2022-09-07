from aiogram.dispatcher.filters.state import State, StatesGroup


class SettingsPaypalFSM(StatesGroup):
    mode = State()
    client_id = State()
    client_secret = State()
