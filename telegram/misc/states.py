from aiogram.fsm.state import State, StatesGroup


class WelcomeStatesGroup(StatesGroup):
    welcome = State()


class CreateProfileStates(StatesGroup):
    start = State()
    name = State()
    age = State()
    sex = State()
    opposite_sex = State()
    university = State()
    description = State()
    photo = State()
