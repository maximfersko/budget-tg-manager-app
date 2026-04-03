from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.repo import DBRepository
from services.statistics_service import StatisticsService

router = Router(name="statistics_handler")


@router.message(Command("statistics"))
async def statistics(message: Message, repo: DBRepository):
    user_id = message.from_user.id

    service = StatisticsService()
    operations = await service.get_salary_statistics_range_date(repo, user_id)

    await message.answer(f"Salary: {operations['salary']:.2f} руб")
