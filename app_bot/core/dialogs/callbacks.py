import logging
import uuid
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.api.entities import ShowMode
from core.states.main_menu import MainMenuStateGroup
from core.states.registration import RegistrationStateGroup
from core.states.station import StationStateGroup
from core.states.support import SupportStateGroup
from core.database.models import User, SupportRequest, Product, Order
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

        # TODO: create invoice link here

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
