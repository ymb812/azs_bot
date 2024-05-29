import logging
from tortoise.functions import Lower
from aiogram import types, Router
from core.database.models import Station


logger = logging.getLogger(__name__)
router = Router(name='Inline-mode router')


@router.inline_query()
async def show_stations(inline_query: types.InlineQuery):
    address = inline_query.query.lower()
    if len(address) == 0:
        return

    stations = await Station.annotate(address_lower=Lower('address')).filter(address_lower__contains=address)

    results = []
    for i, station in enumerate(stations):
        results.append(types.InlineQueryResultArticle(
            id=str(i),
            title=station.address,
            input_message_content=types.InputTextMessageContent(
                message_text=str(station.id),
                parse_mode='HTML',
            )
        ))

    results = results[:50]  # cuz of inline limits
    await inline_query.answer(results, cache_time=3600)  # TODO: CHANGE TO THE PARSER INTERVAL
