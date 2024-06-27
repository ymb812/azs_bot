import logging
from tortoise.expressions import F as F_exp
from aiogram import types, Router, F, Bot
from aiogram_dialog import DialogManager
from core.database.models import User, Order
from core.states.main_menu import MainMenuStateGroup
from core.keyboards.inline import confirm_order_kb
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Basic commands router')


# payment handler - useless
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# payment handler - useless
@router.message(F.successful_payment)
async def handle_successful_payment(message: types.Message, bot: Bot, dialog_manager: DialogManager):
    order_id = message.successful_payment.invoice_payload

    # update order, update user, send data in chat
    await successful_payment(
        order_id=order_id,
        user_id=message.from_user.id,
        bot=bot,
        is_auto_approve=True,
    )

    await dialog_manager.start(MainMenuStateGroup.main_menu)


def get_username_or_link(user: User):
    if user.username:
        user_username = f'@{user.username}'
    else:
        user_username = f'<a href="tg://user?id={user.user_id}">ссылка</a>'

    return user_username


# for tg and card payments
async def successful_payment(
        order_id: str,
        user_id: int,
        bot: Bot,
        is_auto_approve: bool,
        photo_file_id: str = None,
        is_balance_for_profile: bool = False,  # balance for profile
        is_balance_debit: bool = False,  # to auto debit the balance
):
    order = await Order.get(id=order_id)
    user = await User.get(user_id=user_id)

    # handle azs orders
    if not is_balance_for_profile:
        if is_auto_approve:
            # update order and user data instantly if via tg_payment
            order.is_paid = True
            user.payment_amount = F_exp('payment_amount') + order.total_price
            user.refills_amount = F_exp('refills_amount') + 1
            if is_balance_debit:
                user.balance = F_exp('balance') - order.total_price

            topic_name = f'Заказ | Списание с баланса'
            reply_markup = None
            info_text_for_user = f'Оплата прошла успешно, можете вставить пистолет в бак и заправляться. Если будут сложности напишите нашему менеджеру или наберите по телефону'
        else:
            topic_name = f'Заказ | Перевод по карте'
            reply_markup = confirm_order_kb(order_id=order_id)
            info_text_for_user = f'Оплата заправки отправлена на проверку.'

        topic_text = f'Заказ <code>{order.id}</code> от пользователя {get_username_or_link(user=user)}\n\n' \
                     f'<b>Топливо:</b> {(await order.product).name}\n' \
                     f'<b>Кол-во:</b> {order.amount} л\n' \
                     f'<b>Адрес:</b> {(await order.station).address}\n\n' \
                     f'<b>Оплачено: {order.total_price} рублей</b>'

    # handle balance for profile
    else:
        topic_name = f'Пополнение баланса'
        reply_markup = confirm_order_kb(order_id=order_id)
        info_text_for_user = f'Оплата пополнения отправлена на проверку.'
        topic_text = f'Пополнение баланса <code>{order.id}</code> от пользователя {get_username_or_link(user=user)}\n\n' \
                     f'<b>Сумма:</b> {order.total_price} рублей\n'


    # send data to new topic in managers chat
    topic = await bot.create_forum_topic(
        chat_id=settings.managers_chat_id,
        name=topic_name,
    )
    if not photo_file_id:
        await bot.send_message(
            chat_id=settings.managers_chat_id,
            message_thread_id=topic.message_thread_id,
            text=topic_text,
            reply_markup=reply_markup,
        )
    elif photo_file_id:
        await bot.send_photo(
            chat_id=settings.managers_chat_id,
            message_thread_id=topic.message_thread_id,
            caption=topic_text,
            photo=photo_file_id,
            reply_markup=reply_markup,
        )

    # send info msg to the user
    await bot.send_message(
        chat_id=user_id,
        text=info_text_for_user,
    )

    await order.save()
    await user.save()

    return order
