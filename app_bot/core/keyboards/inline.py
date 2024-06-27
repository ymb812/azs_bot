from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.texts import _


def mailing_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('MAILING_BUTTON'), callback_data='start_mailing')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def confirm_order_kb(order_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('APPROVE_BUTTON'), callback_data=f'approve_{order_id}')
    kb.button(text=_('REJECT_BUTTON'), callback_data=f'reject_{order_id}')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
