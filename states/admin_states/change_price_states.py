from aiogram.dispatcher.filters.state import State, StatesGroup


class ChangePriceFSM(StatesGroup):
    one_day = State()
    three_day = State()
    week_day = State()
    month_day = State()
    king_chat = State()
