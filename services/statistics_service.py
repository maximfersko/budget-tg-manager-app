from datetime import datetime

from database.repo import DBRepository


class StatisticsService:

    def get_salary_statistics(self, repo: DBRepository,
                            user_id: int, start_date: datetime, end_date: datetime):
        pass