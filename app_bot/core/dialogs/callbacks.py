import logging
import uuid
from aiogram.types import CallbackQuery, Message, LabeledPrice
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.api.entities import ShowMode
from core.handlers.payment import successful_payment
from core.states.main_menu import MainMenuStateGroup
from core.states.registration import RegistrationStateGroup
from core.states.station import StationStateGroup
from core.states.favourite_stations import FavouriteStationsStateGroup
from core.states.support import SupportStateGroup
from core.dialogs.custom_content import get_dialog_data
from core.database.models import User, SupportRequest, Product, Order, FavouriteStation
from core.utils.texts import _
from settings import settings

logger = logging.getLogger(__name__)


class RegistrationCallbackHandler:
    @staticmethod
    async def entered_fio(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value,
    ):
        # correct checker
        fio = message.text.strip()
        for i in fio:
            if i.isdigit():
                return
        if fio.isdigit() or len(fio.split(' ')) > 5:
            return

        value: str
        dialog_manager.dialog_data['fio'] = value
        await dialog_manager.switch_to(state=RegistrationStateGroup.phone_input)


    @staticmethod
    async def entered_phone(
            message: Message,
            widget: MessageInput,
            dialog_manager: DialogManager,
    ):
        if message.contact:
            phone = message.contact.phone_number
        else:
            phone = message.text.strip()

        dialog_manager.dialog_data['phone'] = phone
        await dialog_manager.switch_to(state=RegistrationStateGroup.confirm)


    @staticmethod
    async def confirm_data(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        user = await User.get(user_id=callback.from_user.id)
        user.is_registered = True
        user.fio = dialog_manager.dialog_data['fio']
        user.phone = dialog_manager.dialog_data['phone']
        await user.save()

        await dialog_manager.start(state=MainMenuStateGroup.main_menu, show_mode=ShowMode.DELETE_AND_SEND)


class StationCallbackHandler:
    @staticmethod
    async def entered_station_id(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value,
    ):
        dialog_manager.dialog_data['station_id'] = value
        await dialog_manager.switch_to(state=StationStateGroup.confirm_station)


    @staticmethod
    async def list_of_products(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        station_id = dialog_manager.dialog_data['station_id']

        products = await Product.filter(station_id=station_id)
        if not products:
            await callback.message.answer(text=f'Нет данных по заправке с id={station_id} - обратитесь в поддержку')
            logger.critical(f'There is no product info station_id={station_id}')
            return

        await dialog_manager.switch_to(state=StationStateGroup.pick_product)


    @staticmethod
    async def add_or_remove_favourite(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        favourite_station = await FavouriteStation.get_or_none(
            user_id=dialog_manager.event.from_user.id,
            station_id=dialog_manager.dialog_data['station_id']
        )
        if widget.widget_id == 'add_favourite':
            if not favourite_station:
                await FavouriteStation.create(
                    user_id=dialog_manager.event.from_user.id,
                    station_id=dialog_manager.dialog_data['station_id']
                )

        elif widget.widget_id == 'remove_favourite':
            if favourite_station:
                await favourite_station.delete()


    @staticmethod
    async def pick_other_station(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        # start favourite or go to inline
        if get_dialog_data(dialog_manager=dialog_manager, key='from_favourite'):
            await dialog_manager.start(state=FavouriteStationsStateGroup.menu)
        else:
            await dialog_manager.switch_to(state=StationStateGroup.input_station)


    @staticmethod
    async def selected_product(
            callback: CallbackQuery,
            widget: Select,
            dialog_manager: DialogManager,
            item_id: int
    ):
        dialog_manager.dialog_data['product_id'] = item_id
        await dialog_manager.switch_to(state=StationStateGroup.input_amount)


    @staticmethod
    async def entered_amount(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value,
    ):
        dialog_manager.dialog_data['amount'] = value
        await dialog_manager.switch_to(state=StationStateGroup.confirm_order)


    @staticmethod
    async def create_order(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        order = await Order.create(
            id=uuid.uuid4(),
            user_id=callback.from_user.id,
            station_id=dialog_manager.dialog_data['station_id'],
            product_id=dialog_manager.dialog_data['product_id'],
            amount=dialog_manager.dialog_data['amount'],
            total_price=dialog_manager.dialog_data['total_price'],
        )
        dialog_manager.dialog_data['order_id'] = str(order.id)

        # create invoice link here
        invoice_link = await dialog_manager.event.bot.create_invoice_link(
            title=f'Заказ {order.id}',
            description=f'Топливо: {dialog_manager.dialog_data["product_name"]}\n'
                        f'Кол-во: {dialog_manager.dialog_data["amount"]} л\n'
                        f'Адрес: {dialog_manager.dialog_data["station_address"]}',
            provider_token=settings.payment_token.get_secret_value(),
            currency='rub',
            prices=[LabeledPrice(label=f'Заказ {order.id}', amount=round(dialog_manager.dialog_data['total_price'] * 100))],
            payload=f'{order.id}',
        )
        dialog_manager.dialog_data['invoice_link'] = invoice_link

        await dialog_manager.switch_to(state=StationStateGroup.pick_payment)


    @staticmethod
    async def delete_order(
            callback: CallbackQuery,
            widget: Button,
            dialog_manager: DialogManager,
    ):
        await Order.filter(id=dialog_manager.dialog_data['order_id']).delete()

        if widget.widget_id == 'main_menu':
            await dialog_manager.start(state=MainMenuStateGroup.main_menu)
        elif widget.widget_id == 'manager_support':
            await dialog_manager.start(state=SupportStateGroup.question_input)


    @staticmethod
    async def entered_payment_photo(
            message: Message,
            widget: MessageInput,
            dialog_manager: DialogManager,
    ):
        # handle file input
        photo_file_id = None
        if message.photo:
            photo_file_id = message.photo[-1].file_id
        dialog_manager.dialog_data['photo_file_id'] = photo_file_id

        await dialog_manager.switch_to(state=StationStateGroup.confirm_payment_photo)


    @staticmethod
    async def successful_card_payment(
            callback: CallbackQuery,
            widget: Button,
            dialog_manager: DialogManager,
    ):
        # update order, update user, send data in chat
        await successful_payment(
            order_id=dialog_manager.dialog_data['order_id'],
            user_id=callback.from_user.id,
            bot=dialog_manager.event.bot,
            is_tg_payment=False,
        )

        await dialog_manager.start(MainMenuStateGroup.main_menu)


class SupportCallbackHandler:
    @staticmethod
    async def entered_question(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value,
    ):
        question = message.text.strip()
        await SupportRequest.create(
            user_id=message.from_user.id,
            text=question,
        )

        # send question to admin
        if message.from_user.username:
            username = f'@{message.from_user.username}'
        else:
            username = f'<a href="tg://user?id={message.from_user.id}">ссылка</a>'
        await dialog_manager.middleware_data['bot'].send_message(
            chat_id=settings.admin_chat_id, text=_('QUESTION_FROM_USER', username=username, question=question)
        )

        await message.answer(text=_('QUESTION_INFO'))
        await dialog_manager.start(state=MainMenuStateGroup.main_menu)


class FavouriteStationsCallbackHandler:
    @staticmethod
    async def selected_station(
            callback: CallbackQuery,
            widget: Select,
            dialog_manager: DialogManager,
            item_id: int
    ):
        await dialog_manager.start(
            state=StationStateGroup.confirm_station,
            data={'from_favourite': True, 'station_id': item_id}
        )
