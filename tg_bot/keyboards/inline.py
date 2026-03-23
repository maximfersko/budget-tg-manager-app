from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_banks_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="T-Bank", callback_data="bank_tinkoff"),
            InlineKeyboardButton(text="Alfa-Bank", callback_data="bank_alfa"),
        ],
        [
            InlineKeyboardButton(text="Sberbank", callback_data="bank_sber")
        ]
    ])
