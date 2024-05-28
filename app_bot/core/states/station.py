from aiogram.fsm.state import State, StatesGroup


class StationStateGroup(StatesGroup):
    input_station = State()
    confirm_station = State()
    pick_product = State()
    input_amount = State()
