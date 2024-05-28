import logging
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.api.entities import ShowMode
from core.states.main_menu import MainMenuStateGroup
from core.states.registration import RegistrationStateGroup
from core.states.station import StationStateGroup
from core.database.models import User, SupportRequest, Station, Dispatcher, Post
from core.utils.texts import _
from parser.stations_parser import StationsParser
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

        # request for station products
        # TODO: REQUEST TO DB
        # try:
        #     products = await StationsParser.products_parser(station_id=station_id)
        # except Exception as e:
        #     await callback.message.answer(text='Не удалось получить данные по данной заправке - обратитесь в поддержку')
        #     # TODO: GET OLD DB DATA AND SEND NOTIFICATION
        #     logger.critical(f'Product info cannot be received for station_id={station_id}', exc_info=e)
        #     return

        # TODO: CACHE TO DB

        await dialog_manager.switch_to(state=StationStateGroup.pick_product)


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
