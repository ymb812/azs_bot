from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Start, Select
from core.dialogs.custom_content import CustomPager
from core.dialogs.callbacks import FavouriteStationsCallbackHandler
from core.dialogs.getters import get_favourite_stations
from core.states.main_menu import MainMenuStateGroup
from core.states.favourite_stations import FavouriteStationsStateGroup
from core.utils.texts import _


favourite_stations_dialog = Dialog(
    # menu
    Window(
        Const(text='Выберите АЗС 👇'),
        CustomPager(
            Select(
                id='_favourite_stations_select',
                items='favourite_stations',
                item_id_getter=lambda item: item.id,
                text=Format(text='{item.name}'),
                on_click=FavouriteStationsCallbackHandler.selected_station,
            ),
            id='favourite_stations_group',
            height=5,
            width=1,
            hide_on_single_page=True,
        ),
        Start(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=MainMenuStateGroup.main_menu),
        getter=get_favourite_stations,
        state=FavouriteStationsStateGroup.menu
    ),
)
