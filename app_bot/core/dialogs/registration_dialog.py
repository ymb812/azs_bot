from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.kbd import Button, SwitchTo, RequestContact
from aiogram_dialog.widgets.input import TextInput, MessageInput
from core.dialogs.getters import get_input_data
from core.dialogs.callbacks import RegistrationCallbackHandler
from core.states.registration import RegistrationStateGroup
from core.utils.texts import _


registration_dialog = Dialog(
    # general registration
    Window(
        Const(text='Приветственное сообщение.\n\nПожалуйста, зарегистрируйтесь для доступа к боту'),
        SwitchTo(Const(text=_('Зарегистрироваться')), id='go_to_fio', state=RegistrationStateGroup.fio_input),
        state=RegistrationStateGroup.general_registration,
    ),

    # fio input
    Window(
        Const(text=_('FIO_INPUT')),
        TextInput(
            id='fio_input',
            type_factory=str,
            on_success=RegistrationCallbackHandler.entered_fio,
        ),
        state=RegistrationStateGroup.fio_input,
    ),

    # phone input
    Window(
        Const(text=_('PHONE_INPUT')),
        RequestContact(Const(text=_('SHARE_CONTACT_BUTTON'))),
        MessageInput(func=RegistrationCallbackHandler.entered_phone),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_fio', state=RegistrationStateGroup.fio_input),
        markup_factory=ReplyKeyboardFactory(resize_keyboard=True),
        state=RegistrationStateGroup.phone_input,
    ),

    # confirm
    Window(
        Format(text=_('CONFIRM_INPUT_DATA',
                      fio='{data[fio]}',
                      phone='{data[phone]}')
               ),
        Button(Const(text=_('CONFIRM_BUTTON')), id='end_of_reg', on_click=RegistrationCallbackHandler.confirm_data),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_phone', state=RegistrationStateGroup.phone_input),
        getter=get_input_data,
        state=RegistrationStateGroup.confirm,
    ),
)
