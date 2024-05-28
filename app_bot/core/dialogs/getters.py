from aiogram_dialog import DialogManager
from core.database.models import User, Station


async def get_input_data(dialog_manager: DialogManager, **kwargs):
    return {'data': dialog_manager.dialog_data}


async def get_user_data(dialog_manager: DialogManager, **kwargs):
    user = await User.get(user_id=dialog_manager.event.from_user.id)

    return {
        'user': user
    }
