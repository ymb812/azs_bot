from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Start, SwitchTo
from aiogram_dialog.widgets.input import TextInput, MessageInput
from core.dialogs.callbacks import StationCallbackHandler
from core.dialogs.getters import get_input_data, get_bot_data, get_station_data, get_products_by_station
from core.states.main_menu import MainMenuStateGroup
from core.states.station import StationStateGroup
from core.utils.texts import _


station_dialog = Dialog(
    # input_station
    Window(
        Format(text=_('INPUT_STATION', bot_username='{bot_username}')),
        TextInput(
            id='input_exhibit',
            type_factory=int,
            on_success=StationCallbackHandler.entered_station_id
        ),
        Start(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=MainMenuStateGroup.main_menu),
        getter=get_bot_data,
        state=StationStateGroup.input_station
    ),

    # confirm_station
    Window(
        Format(text='Вы выбрали\n\n'
                    '<b>{station.name}</b>\n'
                    '<b>Адрес:</b> {station.address}'),
        Button(Const(text=_('CONFIRM_BUTTON')), id='go_to_input_product', on_click=StationCallbackHandler.list_of_products),
        SwitchTo(Const(text='Выбрать другую АЗС'), id='go_to_input_station', state=StationStateGroup.input_station),
        getter=get_station_data,
        state=StationStateGroup.confirm_station
    ),

    # TODO: NEXT WINDOWS: 1. LIST OF PRODUCTS (VIA BUTTONS) 2. INPUT AMOUNT 3. CONFIRM 4. PAYMENT...
    # pick_product
    Window(
        Format(text='Вы выбрали:\n\n'
                    '<b>{station.name}</b>\n'
                    '<b>Адрес:</b> {station.address}'),
        SwitchTo(Const(text=_('CONFIRM_BUTTON')), id='go_to_input_product', state=StationStateGroup.pick_product),
        SwitchTo(Const(text='Выбрать другую АЗС'), id='go_to_input_station', state=StationStateGroup.input_station),
        getter=get_products_by_station,
        state=StationStateGroup.pick_product
    ),
)
