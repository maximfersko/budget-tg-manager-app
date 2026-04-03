import os

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from core.logger import logger
from dto.user_dto import UserDto
from tg_bot.keyboards.callbacks import BANK_PREFIX
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


@router.message(Command("test"))
async def test(message: Message, state: FSMContext):
    from workers.tasks.notifications import task_test
    
    task = task_test.apply_async(args=[message.from_user.id])
    await message.answer(f"Задача отправлена в очередь Celery\nTask ID: {task.id}")


@router.callback_query(IncomeStates.waiting_for_bank, F.data.startswith(BANK_PREFIX))
async def process_bank_selection(callback_query: CallbackQuery, state: FSMContext):
    bank_code = callback_query.data.split("_")[1]

    await state.update_data(bank=bank_code)

    await callback_query.message.edit_text(
        text=" send to file CSV"
    )

    await state.set_state(IncomeStates.waiting_for_document)


@router.message(IncomeStates.waiting_for_document, F.document)
async def process_income_file(message: Message, state: FSMContext, bot: Bot):
    logger.info(message.model_dump())

    if not message.document.mime_type == "text/csv":
        await message.answer("Error! Please send file with extension .csv")
        return

    csv_doc = message.document
    filename = message.document.file_name

    user_data = await state.get_data()
    bank_code = user_data.get("bank")
    
    if bank_code not in ["tinkoff", "alfa"]:
        await message.answer("Unknown bank or not supported yet.")
        await state.clear()
        return

    await message.answer(f"{message.from_user.first_name}, your file is being processed...")

    user_info = UserDto(
        user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username
    )

    from workers.tasks.process_file import process_file
    task = process_file.delay(
        file_id=csv_doc.file_id,
        user_info=user_info.model_dump(),
        file_name=filename,
        bank_code=bank_code
    )

    logger.info(f"Task {task.id} sent to Celery for user {message.from_user.id}")

    await message.answer(
        f"✅ File sent to processing queue\n"
        f"Task ID: {task.id}\n"
        f"You will be notified when processing is complete."
    )

    await state.clear()
