import logging
from tortoise.expressions import F as F_exp
from aiogram import types, Router, F, Bot
from aiogram_dialog import DialogManager
from core.database.models import User, Order
from core.states.main_menu import MainMenuStateGroup
from core.keyboards.inline import confirm_kb
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Basic commands router')


# payment handler
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def handle_successful_payment(message: types.Message, bot: Bot, dialog_manager: DialogManager):
    order_id = message.successful_payment.invoice_payload

    # update order, update user, send data in chat
    await successful_payment(
        order_id=order_id,
        user_id=message.from_user.id,
        bot=bot,
        is_tg_payment=True,
    )

    await dialog_manager.start(MainMenuStateGroup.main_menu)


def get_username_or_link(user: User):
    if user.username:
        user_username = f'@{user.username}'
    else:
        user_username = f'<a href="tg://user?id={user.user_id}">ссылка</a>'

    return user_username


# for tg and card payments
async def successful_payment(order_id: str, user_id: int, bot: Bot, is_tg_payment: bool):
    order = await Order.get(id=order_id)
    user = await User.get(user_id=user_id)

    if is_tg_payment:
        # update order and user data instantly if via tg_payment
        order.is_paid = True
        user.payment_amount = F_exp('payment_amount') + order.total_price
        user.refills_amount = F_exp('refills_amount') + 1

        topic_name = f'Заказ | ЮКасса'
        reply_markup = None
        info_text_for_user = f'Заказ <code>{order.id}</code> успешно оплачен и отправлен менеджерам!'

    else:
        topic_name = f'Заказ | Перевод по карте'
        reply_markup = confirm_kb(order_id=order_id)
        info_text_for_user = f'Заказ <code>{order.id}</code> успешно отправлен на модерацию!'

    topic_text = f'Заказ <code>{order.id}</code> от пользователя {get_username_or_link(user=user)}\n\n' \
                 f'<b>Топливо:</b> {(await order.product).name}\n' \
                 f'<b>Кол-во:</b> {order.amount} л\n' \
                 f'<b>Адрес:</b> {(await order.station).address}\n\n' \
                 f'<b>Оплачено: {order.total_price} рублей</b>'


    # send data to new topic in managers chat
    topic = await bot.create_forum_topic(
        chat_id=settings.managers_chat_id,
        name=topic_name,
    )
    await bot.send_message(
        chat_id=settings.managers_chat_id,
        message_thread_id=topic.message_thread_id,
        text=topic_text,
        reply_markup=reply_markup,
    )

    # send info msg to the user
    await bot.send_message(
        chat_id=user_id,
        text=info_text_for_user,
    )

    await order.save()
    await user.save()
