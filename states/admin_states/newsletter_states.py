from aiogram.dispatcher.filters.state import State, StatesGroup


class NewsletterFSM(StatesGroup):
    get_message = State()
    go_newsletter = State()
