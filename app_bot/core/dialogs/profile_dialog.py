from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Start
from core.dialogs.getters import get_user_data
from core.states.main_menu import MainMenuStateGroup
from core.states.profile import ProfileStateGroup
from core.utils.texts import _


profile_dialog = Dialog(
    # menu
    Window(
        Format(
            text='<b>Профиль</b>\n\n'
                 '<b>ФИО:</b> {user.fio}\n'
                 '<b>Телефон:</b> {user.phone}\n'
                 '<b>Количество заправок:</b> {user.refills_amount}'),
        Start(Const(text=_('BACK_BUTTON')), id='go_to_main_menu', state=MainMenuStateGroup.main_menu),
        getter=get_user_data,
        state=ProfileStateGroup.menu,
    ),
)
