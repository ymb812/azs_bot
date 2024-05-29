import pytz
from datetime import datetime
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware, types
from core.database.models import User


class UpdateUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data['event_from_user']

        tz = pytz.timezone('Europe/Moscow')
        await User.filter(user_id=user.id).update(
            last_activity=tz.localize(datetime.now()),
        )

        return await handler(event, data)
