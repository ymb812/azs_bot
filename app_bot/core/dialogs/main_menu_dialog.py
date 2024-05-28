from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Start, SwitchTo
from core.states.main_menu import MainMenuStateGroup
from core.states.profile import ProfileStateGroup
from core.states.station import StationStateGroup
from core.states.favourite_stations import FavouriteStationsStateGroup
from core.states.support import SupportStateGroup
from core.utils.texts import _


main_menu_dialog = Dialog(
    # main menu
    Window(
        Const(text='<b>Главное меню</b>'),
        Start(Const(text='Мой профиль'), id='profile', state=ProfileStateGroup.menu),
        Start(Const(text='Найти АЗС'), id='station_work', state=StationStateGroup.input_station),
        Start(Const(text='Избранные АЗС'), id='favourite_stations', state=FavouriteStationsStateGroup.menu),
        Start(Const(text='Связаться с менеджером'), id='days_1', state=SupportStateGroup.question_input),
        state=MainMenuStateGroup.main_menu,
    ),
)
