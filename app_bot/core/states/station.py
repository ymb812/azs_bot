from aiogram.fsm.state import State, StatesGroup


class StationStateGroup(StatesGroup):
    input_station = State()
    confirm_station = State()
    input_product = State()
    input_amount = State()
