from aiogram.dispatcher.filters.state import State, StatesGroup


class RegisterFSM(StatesGroup):
    age = State()
    user_sex = State()
    interesting_sex = State()
    city = State()
    name_user = State()
    description_user = State()
    photo = State()


class FakeRegisterFSM(StatesGroup):
    user_id = State()
    age = State()
    user_sex = State()
    interesting_sex = State()
    city = State()
    name_user = State()
    description_user = State()
    photo = State()
