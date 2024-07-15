from aiogram.fsm.state import State, StatesGroup


class ProfileStateGroup(StatesGroup):
    menu = State()
    balance_input = State()
