from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Start, SwitchTo, Select, Column, Url
from aiogram_dialog.widgets.input import TextInput
from core.dialogs.callbacks import StationCallbackHandler
from core.dialogs.getters import get_bot_data, get_station_data, get_products_by_station, get_order_data, get_input_data
from core.states.main_menu import MainMenuStateGroup
from core.states.station import StationStateGroup
from core.states.support import SupportStateGroup
from core.utils.texts import _


station_dialog = Dialog(
    # input_station
    Window(
        Format(text=_('INPUT_STATION', bot_username='{bot_username}')),
        TextInput(
            id='input_station',
            type_factory=int,
            on_success=StationCallbackHandler.entered_station_id
        ),
        Start(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=MainMenuStateGroup.main_menu),
        getter=get_bot_data,
        state=StationStateGroup.input_station
    ),

    # confirm_station
    Window(
        Format(text='<b>{station.name}</b>\n'
                    '<b>Адрес:</b> {station.address}'),
        Button(Const(text=_('CONFIRM_BUTTON')), id='go_to_input_product', on_click=StationCallbackHandler.list_of_products),
        # TODO: ADD BUTTON 'Добавить АЗС в избранные' (FavouriteStation)
        SwitchTo(Const(text='Выбрать другую АЗС'), id='go_to_input_station', state=StationStateGroup.input_station),
        getter=get_station_data,
        state=StationStateGroup.confirm_station
    ),

    # pick_product
    Window(
        Format(text='Выберите топливо 👇'),
        Column(
            Select(
                    id='_product_select',
                    items='products',
                    item_id_getter=lambda item: item.id,
                    text=Format(text='{item.name}'),
                    on_click=StationCallbackHandler.selected_product,
            ),
        ),
        SwitchTo(Const(text='Выбрать другую АЗС'), id='go_to_input_station', state=StationStateGroup.input_station),
        getter=get_products_by_station,
        state=StationStateGroup.pick_product
    ),

    # input_amount
    Window(
        Format(text='Введите число - количество литров'),
        TextInput(
            id='input_amount',
            type_factory=float,
            on_success=StationCallbackHandler.entered_amount
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_pick_product', state=StationStateGroup.pick_product),
        getter=get_bot_data,
        state=StationStateGroup.input_amount
    ),

    # confirm_order
    Window(
        Format(text='<b>Топливо:</b> {product.name}\n'
                    '<b>Кол-во:</b> {amount} л\n'
                    '<b>Адрес:</b> {station.address}\n\n'
                    '<b>К оплате: {total_price} рублей</b>'),
        Button(Const(text=_('CONFIRM_BUTTON')), id='create_order', on_click=StationCallbackHandler.create_order),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_input_amount', state=StationStateGroup.input_amount),
        getter=get_order_data,
        state=StationStateGroup.confirm_order
    ),

    # pick_payment
    Window(
        Const(text='<b>Выберите вариант оплаты или другое действие</b>'),
        Url(Const(text='💳 Юкасса'),  url=Format('vk.com')),  # TODO: url=Format(text='data[invoice_link]')),
        SwitchTo(Const(text='💳 Перевод по номеру карты'), id='card_photo', state=StationStateGroup.input_payment_photo),
        Button(Const(text='Связаться с менеджером'), id='manager_support', on_click=StationCallbackHandler.delete_order),
        Button(Const(text='Вернуться в меню'), id='main_menu', on_click=StationCallbackHandler.delete_order),
        getter=get_input_data,
        state=StationStateGroup.pick_payment,
    ),
)
