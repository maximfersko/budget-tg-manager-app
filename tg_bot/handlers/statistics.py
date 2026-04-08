import re
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from core.logger import logger
from database.repo import DBRepository
from services.statistics_service import StatisticsService

router = Router(name="statistics_handler")


def _parse_date_from_mess_args(command: CommandObject) -> (datetime, datetime):
    start_date = None
    end_date = None

    if command.args:
        try:
            part_date = command.args.strip().split('-')
            if len(part_date) == 2:
                start_date = datetime.strptime(part_date[0].strip(), "%d.%m.%Y")
                end_date = datetime.strptime(part_date[1].strip(), "%d.%m.%Y")
                # Устанавливаем конец дня для конечной даты
                end_date = end_date.replace(hour=23, minute=59, second=59)
                logger.info(f'Period: {start_date} - {end_date}')
        except ValueError:
            return None, None
    return start_date, end_date


@router.message(Command("stats"))
async def stats(message: Message, repo: DBRepository, command: CommandObject):
    logger.info(message.model_dump())
    start_date, end_date = _parse_date_from_mess_args(command)
    
    if command.args and (start_date is None or end_date is None):
        await message.answer("correct format: `18.07.2024-18.08.2026`", parse_mode="Markdown")
        return

    logger.info(f'Part date: {start_date, end_date}')

    stat_service = StatisticsService()
    result = await stat_service.get_base_stat(repo, message.from_user.id, start_date, end_date)

    await message.answer(
        f"[STATISTICS]\n\n"
        f"Salary: {result['salary']} RUB\n"
        f"Total income: {result['sum_income']} RUB\n"
        f"Total expenses: {result['sum_expense']} RUB\n"
        f"Balance: {result['balance']} RUB\n"
        f"Avg expense: {result['avg_expense']} RUB\n\n"
        f"Transactions: {result['transactions_count']}\n"
        f"Income operations: {result['income_count']}\n"
        f"Expense operations: {result['expense_count']}\n"
        f"Internal transfers excluded: {result.get('internal_transfers_excluded', 0)}"
    )


@router.message(Command("categories"))
async def categories(message: Message, repo: DBRepository, command: CommandObject):
    logger.info(message.model_dump())

    stat_service = StatisticsService()
    result = await stat_service.get_categories_stat(repo, message.from_user.id)

    expense_text = "[TOP EXPENSE CATEGORIES]\n\n"
    for category, data in result['top_expense_categories'].items():
        expense_text += (
            f"{category}:\n"
            f"  Amount: {data['amount']} RUB\n"
            f"  Percentage: {data['percentage']}%\n"
            f"  Operations: {data['count_operations']}\n\n"
        )

    income_text = "[TOP INCOME CATEGORIES]\n\n"
    for category, data in result['top_income_categories'].items():
        income_text += (
            f"{category}:\n"
            f"  Amount: {data['amount']} RUB\n"
            f"  Percentage: {data['percentage']}%\n"
            f"  Operations: {data['count_operations']}\n\n"
        )

    await message.answer(expense_text)
    await message.answer(income_text)
