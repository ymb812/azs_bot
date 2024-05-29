import logging
from aiogram import Bot, types, Router, F, enums
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram_dialog import DialogManager, StartMode
from core.states.main_menu import MainMenuStateGroup
from core.states.registration import RegistrationStateGroup
from core.utils.texts import set_user_commands, set_admin_commands, _
from core.database.models import User


logger = logging.getLogger(__name__)
router = Router(name='Start router')


@router.message(Command(commands=['start']), StateFilter(None))
async def start_handler(message: types.Message, bot: Bot, state: FSMContext, dialog_manager: DialogManager):
    if message.chat.type != enums.ChatType.PRIVATE:
        return

    await state.clear()
    try:
        await dialog_manager.reset_stack()
    except:
        pass

    # add basic info to db
    await User.update_data(
        user_id=message.from_user.id,
        username=message.from_user.username,
    )

    user = await User.get(user_id=message.from_user.id)

    if user.status == 'admin':
        await set_admin_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))
    else:
        await set_user_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))

    # start general registration or going to the main menu if registered
    if user.is_registered:
        await dialog_manager.start(state=MainMenuStateGroup.main_menu, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(state=RegistrationStateGroup.general_registration, mode=StartMode.RESET_STACK)
