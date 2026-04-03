from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from sqlalchemy import BigInteger

from core.logger import logger
from database.models import Operation
from database.repo import DBRepository

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', None)


class StatisticsService:

    async def get_salary_statistics_range_date(
            self,
            repo: DBRepository,
            user_id: BigInteger,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> dict:
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        operations: list[Operation] = await repo.get_user_operations(user_id)

        df = pd.DataFrame([
            {k: v for k, v in op.__dict__.items() if k != '_sa_instance_state'}
            for op in operations
        ])

        salary = df[(df['raw_category'] == 'Зарплата') & (df['amount'] > 0.0)]['amount'].sum()

        logger.info(f"df {df.head(10).to_string()}")

        logger.info(f"Operation count: {len(operations)}")

        return {
            'salary': salary
        }
