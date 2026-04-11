from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot.keyboards.callbacks import (
    BANK_TINKOFF, BANK_ALFA,
    STATS_MONTH, STATS_YEAR, STATS_CUSTOM,
    OP_EDIT, OP_DELETE, OP_CANCEL
)


def get_banks_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="T-Bank", callback_data=BANK_TINKOFF),
            InlineKeyboardButton(text="Alfa-Bank", callback_data=BANK_ALFA),
        ],
    ])


def get_statistics_period_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="This month", callback_data=STATS_MONTH),
            InlineKeyboardButton(text="This year", callback_data=STATS_YEAR)
        ],
        [
            InlineKeyboardButton(text="Custom period", callback_data=STATS_CUSTOM)
        ]
    ])


def get_operation_actions_keyboard(operation_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Edit", callback_data=f"{OP_EDIT}_{operation_id}"),
            InlineKeyboardButton(text="Delete", callback_data=f"{OP_DELETE}_{operation_id}")
        ],
        [
            InlineKeyboardButton(text="Cancel", callback_data=OP_CANCEL)
        ]
    ])
