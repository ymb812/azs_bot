from aiogram.fsm.state import State, StatesGroup


class StationStateGroup(StatesGroup):
    input_station = State()
    confirm_station = State()
    pick_product = State()
    input_amount = State()
    confirm_order = State()

    pick_payment = State()
    input_payment_photo = State()
    confirm_payment_photo = State()
