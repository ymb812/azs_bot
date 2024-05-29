from aiogram.types import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from core.database.models import User, Station, Product, Settings


async def get_input_data(dialog_manager: DialogManager, **kwargs):
    return {'data': dialog_manager.dialog_data}


async def get_bot_data(dialog_manager: DialogManager, **kwargs):
    return {
        'bot_username': (await dialog_manager.event.bot.get_me()).username
    }


async def get_user_data(dialog_manager: DialogManager, **kwargs):
    user = await User.get(user_id=dialog_manager.event.from_user.id)

    return {
        'user': user
    }


async def get_station_data(dialog_manager: DialogManager, **kwargs):
    station = await Station.get_or_none(id=dialog_manager.dialog_data['station_id'])
    if not station:
        raise ValueError

    return {
        'station': station
    }


async def get_products_by_station(dialog_manager: DialogManager, **kwargs):
    products = await Product.filter(station_id=dialog_manager.dialog_data['station_id'])

    return {
        'products': products
    }


async def get_order_data(dialog_manager: DialogManager, **kwargs):
    product = await Product.get(id=dialog_manager.dialog_data['product_id'])
    station: Station = await product.station
    amount = dialog_manager.dialog_data['amount']
    total_price = round(amount * product.price, 2)

    dialog_manager.dialog_data['total_price'] = total_price
    dialog_manager.dialog_data['product_name'] = product.name
    dialog_manager.dialog_data['station_address'] = station.address

    return {
        'product': product,
        'station': station,
        'amount': amount,
        'total_price': total_price,
    }


async def get_card_data(dialog_manager: DialogManager, **kwargs):
    card_data = await Settings.first()

    return {
        'card_data': card_data,
        'data': dialog_manager.dialog_data,
    }


async def get_payment_photo(dialog_manager: DialogManager, **kwargs):
    media_content = MediaAttachment(ContentType.PHOTO, url=dialog_manager.dialog_data['photo_file_id'])

    return {
        'media_content': media_content,
    }
