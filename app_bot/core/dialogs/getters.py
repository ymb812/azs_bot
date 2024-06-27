from aiogram.types import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from core.database.models import User, Station, Product, Settings, FavouriteStation, Card
from core.dialogs.custom_content import get_dialog_data


async def get_input_data(dialog_manager: DialogManager, **kwargs):
    return {'data': dialog_manager.dialog_data}


async def get_bot_data(dialog_manager: DialogManager, **kwargs):
    return {
        'bot_username': (await dialog_manager.event.bot.get_me()).username
    }


async def get_user_data(dialog_manager: DialogManager, **kwargs):
    user = await User.get(user_id=dialog_manager.event.from_user.id)

    return {
        'user': user,
        'payment_amount': round(user.payment_amount, 2),
    }


async def get_station_data(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data['station_id'] = get_dialog_data(dialog_manager=dialog_manager, key='station_id')
    station = await Station.get_or_none(id=dialog_manager.dialog_data['station_id'])
    if not station:
        raise ValueError

    # check is it favourite
    favourite_station = await FavouriteStation.get_or_none(
        user_id=dialog_manager.event.from_user.id,
        station_id=station.id
    )
    is_favourite = False
    if favourite_station:
        is_favourite = True

    return {
        'station': station,
        'is_favourite': is_favourite,
    }


async def get_products_by_station(dialog_manager: DialogManager, **kwargs):
    products = await Product.filter(station_id=dialog_manager.dialog_data['station_id'])

    return {
        'products': products
    }


# create order_data here
async def get_order_data(dialog_manager: DialogManager, **kwargs):
    product = await Product.get(id=dialog_manager.dialog_data['product_id'])
    station: Station = await product.station
    amount = dialog_manager.dialog_data['amount']

    # count discount_percent
    discount = 1
    settings_data = await Settings.first()
    if settings_data:
        discount = 1 - settings_data.discount_percent / 100
    total_price = round(amount * product.price * discount, 2)

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
    card = await Card.filter(is_hidden=False).order_by('order_priority').first()
    if not card:
        card = await Card.all().order_by('-order_priority').first()

    dialog_manager.dialog_data['card_id'] = card.id

    # handle balance for profile
    if dialog_manager.start_data:
        dialog_manager.dialog_data['is_balance_for_profile'] = dialog_manager.start_data.get('is_balance_for_profile')
    else:
        dialog_manager.dialog_data['is_balance_for_profile'] = False

    total_price = get_dialog_data(dialog_manager=dialog_manager, key='total_price')
    dialog_manager.dialog_data['total_price'] = total_price

    return {
        'card_data': card,
        'total_price': total_price,
    }


async def get_payment_photo(dialog_manager: DialogManager, **kwargs):
    media_content = MediaAttachment(ContentType.PHOTO, url=dialog_manager.dialog_data['photo_file_id'])

    return {
        'media_content': media_content,
    }


async def get_favourite_stations(dialog_manager: DialogManager, **kwargs):
    favourite_stations = await FavouriteStation.filter(user_id=dialog_manager.event.from_user.id)
    stations = [await favourite_station.station for favourite_station in favourite_stations]

    return {
        'favourite_stations': stations
    }
