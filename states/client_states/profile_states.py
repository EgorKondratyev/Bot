from aiogram.dispatcher.filters.state import State, StatesGroup


class PhotoChangeFSM(StatesGroup):
    photo_wait = State()


class DescriptionChangeFSM(StatesGroup):
    description_wait = State()


class NameChangeFSM(StatesGroup):
    name_wait = State()


class AgeChangeFSM(StatesGroup):
    age_wait = State()


class SexChangeFSM(StatesGroup):
    sex_fsm = State()


class SexInterestingChangeFSM(StatesGroup):
    sex_interesting_fsm = State()


class BindingInstagramFSM(StatesGroup):
    binding_instagram_wait = State()
