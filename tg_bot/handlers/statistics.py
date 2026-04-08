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
    from services.ai_service import AIService
    from services.vector_service import VectorService
    
    ai_service = AIService()
    vector_service = VectorService()

    base_stats = await stat_service.get_base_stat(repo, message.from_user.id, start_date, end_date)
    
    from database.models import Operation
    operations: list[Operation] = await repo.get_user_operations(message.from_user.id)
    df = stat_service._filter_statistics_date(operations, start_date, end_date)
    summary_text = stat_service.get_summary_for_ai(base_stats, df)

    old_memories = await vector_service.get_relevant_memories(message.from_user.id, summary_text)
    
    ai_advice = await ai_service.analyze_spending(summary_text, old_memories)

    new_insight = await ai_service.extract_insight(summary_text)
    await vector_service.save_insight(message.from_user.id, new_insight)

    clean_advice = ai_advice.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")

    response = (
        f"*СТАТИСТИКА*\n\n"
        f"Зарплата: {base_stats['salary']} RUB\n"
        f"Доходы: {base_stats['sum_income']} RUB\n"
        f"Расходы: {base_stats['sum_expense']} RUB\n"
        f"Баланс: {base_stats['balance']} RUB\n"
        f"Средний расход: {base_stats['avg_expense']} RUB\n\n"
        f"Транзакций: {base_stats['transactions_count']}\n"
        f"Доходных: {base_stats['income_count']}\n"
        f"Расходных: {base_stats['expense_count']}\n"
        f"Исключено внутренних: {base_stats.get('internal_transfers_excluded', 0)}\n\n"
        f"🤖 *Совет от ИИ:*\n{clean_advice}"
    )

    await message.answer(response, parse_mode="Markdown")


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
