from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Start, SwitchTo
from aiogram_dialog.widgets.input import TextInput, MessageInput
from core.dialogs.getters import get_user_data
from core.dialogs.callbacks import ProfileCallbackHandler
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
                 '<b>Количество заправок:</b> {user.refills_amount}\n'
                 '<b>Сумма заправок:</b> {payment_amount} рублей\n'
                 '<b>Баланс:</b> {balance} рублей'
        ),
        SwitchTo(Const(text='💸 Пополнить баланс'), id='go_to_balance', state=ProfileStateGroup.balance_input),
        Start(Const(text=_('BACK_BUTTON')), id='go_to_main_menu', state=MainMenuStateGroup.main_menu),
        getter=get_user_data,
        state=ProfileStateGroup.menu,
    ),

    # balance_input
    Window(
        Const(text='Введите число - сумма в рублях для пополнения баланса, которым можно пользоваться для мгновенной оплаты в боте'),
        TextInput(
            id='balance_input',
            type_factory=int,
            on_success=ProfileCallbackHandler.entered_balance,
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_profile', state=ProfileStateGroup.menu),
        state=ProfileStateGroup.balance_input,
    ),
)
