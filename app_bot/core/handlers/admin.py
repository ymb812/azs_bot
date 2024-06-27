import json
import logging
from tortoise.expressions import F as F_exp
from aiogram import types, Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from broadcaster import Broadcaster
from core.database.models import User, Order
from core.keyboards.inline import mailing_kb
from core.states.mailing import MailingStateGroup
from core.utils.texts import _
from core.excel.excel_generator import create_excel
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Admin commands router')



@router.message(Command(commands=['send']))
async def start_of_mailing(message: types.Message, state: FSMContext):
    user = await User.get(user_id=message.from_user.id)
    if user.status != 'admin':
        return

    await message.answer(_('INPUT_MAILING_CONTENT'))
    await state.set_state(MailingStateGroup.content_input)


@router.message(MailingStateGroup.content_input)
async def confirm_mailing(message: types.Message, state: FSMContext):
    await message.answer(text=_('CONFIRM_MAILING'), reply_markup=mailing_kb())
    await state.update_data(content=message.model_dump_json(exclude_defaults=True))


@router.callback_query(F.data == 'start_mailing', MailingStateGroup.content_input)
async def admin_team_approve_handler(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    # cuz command is only for 'admin'
    user = await User.get(user_id=callback.from_user.id)
    users_amount = len(await User.all())

    state_data = await state.get_data()

    text = _('MAILING_HAS_BEEN_STARTED', admin_username=callback.from_user.username)
    await callback.message.answer(text=text)

    sent_amount = await Broadcaster.send_content_to_users(bot=bot,
                                                          message=types.Message(**json.loads(state_data['content'])))
    await state.clear()

    await callback.message.answer(text=_('MAILING_IS_COMPLETED', users_amount=users_amount, sent_amount=sent_amount))


@router.message(Command(commands=['stats']))
async def excel_stats(message: types.Message):
    # cuz command is only for 'admin'
    user = await User.get(user_id=message.from_user.id)
    if user.status != 'admin':
        return

    file_in_memory = await create_excel(model=User)
    await message.answer_document(document=types.BufferedInputFile(file_in_memory.read(), filename=settings.excel_file))


# get file_id for broadcaster
@router.message(Command(commands=['get_content']), F.video | F.video_note | F.photo | F.audio | F.animation | F.sticker | F.document)
async def get_hash(message: types.Message):
    if (await User.get(user_id=message.from_user.id)).status != 'admin':
        return

    if message.video:
        hashsum = message.video.file_id
    elif message.video_note:
        hashsum = message.video_note.file_id
    elif message.photo:
        hashsum = message.photo[-1].file_id
    elif message.audio:
        hashsum = message.audio.file_id
    elif message.animation:
        hashsum = message.animation.file_id
    elif message.sticker:
        hashsum = message.sticker.file_id
    elif message.document:
        hashsum = message.document.file_id
    else:
        return

    await message.answer(f'<code>{hashsum}</code>')


@router.callback_query(lambda c: ('approve_' in c.data or 'reject_' in c.data))
async def admin_team_approve_handler(callback: types.CallbackQuery, bot: Bot):
    order_id = callback.data.split('_')[-1]
    order = await Order.get(id=order_id)
    user = await User.get(user_id=order.user_id)

    if 'approve_' in callback.data:
        # handle balance for profile
        if order.is_for_balance:
            order.is_paid = True
            user.balance = F_exp('balance') + order.total_price

            text = f'Баланс успешно пополнен на {order.total_price} рублей'

        else:
            # update order and user data
            order.is_paid = True
            user.payment_amount = F_exp('payment_amount') + order.total_price
            user.refills_amount = F_exp('refills_amount') + 1

            text = f'Оплата прошла успешно, можете вставить пистолет в бак и заправляться. Если будут сложности напишите нашему менеджеру или наберите по телефону'

    elif 'reject_' in callback.data:
        # handle balance for profile
        if order.is_for_balance:
            text = f'Ваша заявка на пополнения баланса <code>{order_id}</code> была отклонена'

        else:
            text = f'Ваш заказ <code>{order_id}</code> был отклонен'

    # delete reply_markup
    await callback.message.edit_reply_markup(reply_markup=None)

    await order.save()
    await user.save()

    # send info to the user
    await bot.send_message(
        chat_id=user.user_id,
        text=text,
    )
