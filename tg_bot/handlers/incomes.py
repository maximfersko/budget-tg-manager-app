import os

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from core.logger import logger
from database.repo import DBRepository
from services.csv_alfa_parser_service import AlfaBankCSVParser
from services.csv_tink_parser_service import TinkoffBankCSVParser
from tg_bot.keyboards.inline import get_banks_keyboard

router = Router(name="incomes_handler")


class IncomeStates(StatesGroup):
    waiting_for_bank = State()
    waiting_for_document = State()


@router.message(Command("incomes"))
async def incomes(message: Message, state: FSMContext):
    logger.info(message.model_dump())


    await message.answer(
        text="Pick your bank",
        reply_markup=get_banks_keyboard()
    )

    await state.set_state(IncomeStates.waiting_for_bank)


@router.callback_query(IncomeStates.waiting_for_bank, F.data.startswith("bank_"))
async def process_bank_selection(callback_query: CallbackQuery, state: FSMContext):
    bank_code = callback_query.data.split("_")[1]
    
    await state.update_data(bank=bank_code)
    
    await callback_query.message.edit_text(
        text=" send to file CSV"
    )
    
    await state.set_state(IncomeStates.waiting_for_document)


@router.message(IncomeStates.waiting_for_document, F.document)
async def process_income_file(message: Message, state: FSMContext, bot: Bot, repo: DBRepository):
    logger.info(message.model_dump())

    if not message.document.mime_type == "text/csv":
        await message.answer("Error! Please send file with extension .csv")
        return

    csv_doc = message.document
    file_path = f"/tmp/incomes_{message.from_user.id}.csv"

    await message.answer(f"{message.from_user.first_name} {message.from_user.last_name} your file processing.. ")

    await bot.download(csv_doc, destination=file_path)

    user_data = await state.get_data()
    logger.info(f"User data: {user_data}")
    bank_code = user_data.get("bank")
    logger.info(f"Bank code: {bank_code}")


    if bank_code == "tinkoff":
        parser = TinkoffBankCSVParser()
    elif bank_code == "alfa":
        parser = AlfaBankCSVParser()
    elif bank_code == "sber":
        await message.answer("pass")
        await state.clear()
        return
    else:
        await message.answer("Unknown bank.")
        await state.clear()
        return

    result_csv = parser.parse_file(file_path)

    await repo.add_user(
        tg_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username
    )

    await repo.add_operations_batch(message.from_user.id, result_csv)

    await message.answer(f"Parsed {len(result_csv)} operations!")

    os.remove(file_path)
    
    await state.clear()
