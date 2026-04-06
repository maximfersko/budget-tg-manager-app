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

    async def get_base_stat(
            self,
            repo: DBRepository,
            user_id: BigInteger,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> dict:
        #TODO: make stat with intervals
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        operations: list[Operation] = await repo.get_user_operations(user_id)

        df = pd.DataFrame([
            {k: v for k, v in op.__dict__.items() if k != '_sa_instance_state'}
            for op in operations
        ])

        income_df = df[df['is_income'] == True]
        expense_df = df[df['is_income'] == False]
        sum_income = income_df['amount'].sum()
        sum_expense = expense_df['amount'].abs().sum()
        balance = sum_income - sum_expense
        avg_expense = expense_df['amount'].abs().mean()
        salary = df[(df['raw_category'] == 'Зарплата') & (df['is_income'] == True)]['amount'].sum()

        #TODO: cache this result, ttl: 8 h, invalidate: if user upload new files
        result = {
            'salary': round(float(salary), 2),
            'sum_income': round(float(sum_income), 2),
            'sum_expense': round(float(sum_expense), 2),
            'balance': round(float(balance), 2),
            'avg_expense': round(float(avg_expense), 2),
            'transactions_count': len(df),
            'income_count': len(income_df),
            'expense_count': len(expense_df)
        }

        logger.info(f"df {df.head(10).to_string()}")

        logger.info(f"result_stats {result}")

        await self.get_categories_stat(repo, user_id, start_date, end_date)

        return result

    async def get_categories_stat(self, repo: DBRepository,
                                  user_id: BigInteger,
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None
                                  ) -> dict:

        operations: list[Operation] = await repo.get_user_operations(user_id)

        df = pd.DataFrame([
            {k: v for k, v in op.__dict__.items() if k != '_sa_instance_state'}
            for op in operations
        ])

        expense_df = df[~df['is_income']]

        top_expense_categories = (
            expense_df.groupby('raw_category')['amount']
            .sum()
            .abs()
            .sort_values(ascending=False)
            .head(10)
        )

        income_df = df[df['is_income']]

        top_income_categories = (
            income_df.groupby('raw_category')['amount']
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        total_expense = expense_df['amount'].sum()
        total_income = income_df['amount'].sum()
        result_categories = {
            'top_expense_categories': {
                k: {
                    'amount': float(round(v, 2)),
                    'percentage': float(round((abs(v) / abs(total_expense)) * 100, 2)),
                    'count_operations': 'k'
                } for k, v in top_expense_categories.items()
            },
            'top_income_categories': {
                k: {
                    'amount': float(round(v, 2)),
                    'percentage': float(round((v / total_income) * 100, 2)),

                } for k, v in top_income_categories.items()
            }
        }
        
        logger.info(f"categories_stat: {result_categories}")

        return result_categories
