from aiogram.dispatcher.filters.state import State, StatesGroup


class Link_Script(StatesGroup):
    add_link = State()
    del_link = State()


class Add_Target(StatesGroup):
    forwarded = State()


class Del_Target(StatesGroup):
    index = State()


class Change_Chat(StatesGroup):
    forwarded = State()


class Add_Admin(StatesGroup):
    admin = State()


class Del_Admin(StatesGroup):
    admin = State()


class Script(StatesGroup):
    add_script = State()
    del_script = State()


class My_link(StatesGroup):
    link = State()


class My_Username(StatesGroup):
    username = State()


class History(StatesGroup):
    link = State()
    count = State()
    iter_count = State()
    sleep = State()