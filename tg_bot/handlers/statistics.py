from datetime import datetime

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from core.logger import logger
from database.models import Operation
from database.repo import DBRepository
from services.ai_service import AIService
from services.statistics_service import StatisticsService
from services.vector_service import VectorService
from workers.tasks.ai_tasks import process_ai_insight_task

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
                logger.info(f"Parsed period: {start_date} - {end_date}")
        except ValueError:
            logger.error("Failed to parse dates from arguments")
            return None, None
    return start_date, end_date


async def stats_logic(message: Message, repo: DBRepository, start_date: datetime, end_date: datetime,
                      categories: list = None):
    logger.info(
        f"Stats handler started for {message.chat.id}: args - {message.text}, {start_date}, {end_date}, {categories}")
    stat_service = StatisticsService()
    ai_service = AIService()
    vector_service = VectorService()

    base_stats = await stat_service.get_base_stat(repo, message.from_user.id, start_date, end_date,
                                                  categories=categories)

    logger.info(f"Base stats: {base_stats}")

    operations: list[Operation] = await repo.get_user_operations(message.from_user.id)
    df_date_filtered = stat_service._filter_statistics_date(operations, start_date, end_date)
    logger.info(f"Filtered stats: {df_date_filtered}")

    summary_text = stat_service.get_summary_for_ai(base_stats, df_date_filtered, is_category_filter=bool(categories))
    if categories:
        summary_text = f"FILTER BY CATEGORIES: {', '.join(categories)}\n" + summary_text

    old_memories = await vector_service.get_relevant_memories(message.from_user.id, summary_text)
    ai_advice = await ai_service.analyze_spending(summary_text, old_memories)

    process_ai_insight_task.delay(
        user_id=message.from_user.id,
        summary_text=summary_text,
        metadata={
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "categories": categories,
            "type": "period_summary"
        }
    )

    clean_advice = ai_advice.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
    period_str = f" ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})" if start_date else ""
    cat_str = f" по категориям: {', '.join(categories)}" if categories else ""

    if categories:
        total_stats = await stat_service.get_base_stat(repo, message.from_user.id, start_date, end_date)
        total_exp = total_stats['sum_expense']
        share = (base_stats['sum_expense'] / total_exp * 100) if total_exp > 0 else 0

        response = (
            f"СТАТИСТИКА{period_str}{cat_str}\n\n"
            f"Расходы по категориям: {base_stats['sum_expense']} RUB\n"
            f"Средний расход: {base_stats['avg_expense']} RUB\n"
            f"Транзакций: {base_stats['transactions_count']}\n"
            f"Доходы (кэшбэк/возвраты): {base_stats['sum_income']} RUB\n\n"
            f"ВСЕГО РАСХОДОВ ЗА ПЕРИОД: {total_exp} RUB\n"
            f"ДОЛЯ В БЮДЖЕТЕ: {share:.1f}%\n"
            f"— — — — — — — — —\n"
            f"Совет от ИИ:\n{clean_advice}"
        )
    else:
        response = (
            f"ОБЩАЯ СТАТИСТИКА{period_str}\n\n"
            f"Зарплата: {base_stats['salary']} RUB\n"
            f"Доходы: {base_stats['sum_income']} RUB\n"
            f"Расходы: {base_stats['sum_expense']} RUB\n"
            f"Баланс: {base_stats['balance']} RUB\n"
            f"Средний расход: {base_stats['avg_expense']} RUB\n\n"
            f"Транзакций: {base_stats['transactions_count']}\n"
            f"— — — — — — — — —\n"
            f"Совет от ИИ:\n{clean_advice}"
        )

    await message.answer(response, parse_mode="Markdown")


@router.message(Command("ai"))
async def handle_ai_command(message: Message, repo: DBRepository, command: CommandObject):
    if not command.args:
        return await message.answer("Напиши запрос после /ai. Пример: /ai статистика за неделю")

    ai_service = AIService()

    user_categories = await repo.get_unique_raw_categories(message.from_user.id)

    intent = await ai_service.parse_user_intent(command.args, categories=user_categories)

    logger.info(f"AI Intent: {intent}")

    if intent["action"] == "stats":
        try:
            start_date = datetime.strptime(intent["start_date"], "%Y-%m-%d") if intent["start_date"] else None
            end_date = datetime.strptime(intent["end_date"], "%Y-%m-%d") if intent["end_date"] else None
            if end_date:
                end_date = end_date.replace(hour=23, minute=59, second=59)

            await stats_logic(message, repo, start_date, end_date, categories=intent.get("categories"))
        except Exception as e:
            logger.error(f"Error executing AI intent: {e}")
            await message.answer("Не удалось обработать запрос.")
    else:
        response = await ai_service.analyze_spending(f"User query: {command.args}", user_memories=[])
        await message.answer(f"Ответ ИИ:\n\n{response}")


@router.message(Command("stats"))
async def stats(message: Message, repo: DBRepository, command: CommandObject):
    start_date, end_date = _parse_date_from_mess_args(command)
    if command.args and (start_date is None or end_date is None):
        await message.answer("Формат: DD.MM.YYYY-DD.MM.YYYY")
        return
    await stats_logic(message, repo, start_date, end_date)


@router.message(Command("stats_simple"))
async def stats_simple(message: Message, repo: DBRepository, command: CommandObject):
    start_date, end_date = _parse_date_from_mess_args(command)
    if command.args and (start_date is None or end_date is None):
        await message.answer("Формат: DD.MM.YYYY-DD.MM.YYYY")
        return
    
    stat_service = StatisticsService()
    base_stats = await stat_service.get_base_stat(repo, message.from_user.id, start_date, end_date)
    
    period_str = f" ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})" if start_date else ""
    
    response = (
        f"СТАТИСТИКА{period_str}\n\n"
        f"Зарплата: {base_stats['salary']} RUB\n"
        f"Доходы: {base_stats['sum_income']} RUB\n"
        f"Расходы: {base_stats['sum_expense']} RUB\n"
        f"Баланс: {base_stats['balance']} RUB\n"
        f"Средний расход: {base_stats['avg_expense']} RUB\n\n"
        f"Транзакций: {base_stats['transactions_count']}\n"
        f"Доходов: {base_stats['income_count']}\n"
        f"Расходов: {base_stats['expense_count']}\n"
        f"Исключено внутренних переводов: {base_stats['internal_transfers_excluded']}"
    )
    
    await message.answer(response)


@router.message(Command("categories"))
async def categories(message: Message, repo: DBRepository, command: CommandObject):
    stat_service = StatisticsService()
    result = await stat_service.get_categories_stat(repo, message.from_user.id)
    expense_text = "ТОП КАТЕГОРИЙ РАСХОДОВ\n\n"
    for cat, data in result['top_expense_categories'].items():
        expense_text += f"{cat}: {data['amount']} RUB ({data['percentage']}%)\n"
    await message.answer(expense_text)
