from datetime import datetime, timedelta
from typing import Optional, List

import pandas as pd
from sqlalchemy import BigInteger

from core.logger import logger
from database.models import Operation
from database.repo import DBRepository

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', None)

from core.config import INTERNAL_TRANSFER_KEYWORDS


class StatisticsService:

    def _is_internal_transfer(self, row) -> bool:
        category = str(row.get('raw_category', '')).lower()
        description = str(row.get('description', '')).lower()

        if category not in ['переводы', 'пополнения', 'пополнение']:
            return False

        for keyword in INTERNAL_TRANSFER_KEYWORDS:
            if keyword in description:
                return True

        return False

    def _filter_statistics_date(self, operations: List[Operation], start_date: datetime, end_date: datetime) -> pd.DataFrame:
        if not operations:
            return pd.DataFrame(columns=['is_income', 'amount', 'date', 'raw_category', 'description'])

        df = pd.DataFrame([
            {k: v for k, v in op.__dict__.items() if k != '_sa_instance_state'}
            for op in operations
        ])

        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        return df

    def _filter_internal_transfers(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        mask = df.apply(lambda row: not self._is_internal_transfer(row), axis=1)
        return df[mask]

    async def get_base_stat(
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

        df = self._filter_statistics_date(operations, start_date, end_date)

        if df.empty:
            return {
                'salary': 0, 'sum_income': 0, 'sum_expense': 0, 'balance': 0,
                'avg_expense': 0, 'transactions_count': 0, 'income_count': 0,
                'expense_count': 0, 'internal_transfers_excluded': 0
            }

        df_filtered = self._filter_internal_transfers(df)

        income_df = df_filtered[df_filtered['is_income'] == True]
        expense_df = df_filtered[df_filtered['is_income'] == False]
        sum_income = income_df['amount'].sum()
        sum_expense = expense_df['amount'].abs().sum()
        balance = sum_income - sum_expense
        avg_expense = expense_df['amount'].abs().mean() if not expense_df.empty else 0
        salary = df_filtered[
            (df_filtered['raw_category'] == 'Зарплата') &
            (df_filtered['is_income'] == True)
            ]['amount'].sum()

        result = {
            'salary': round(float(salary), 2),
            'sum_income': round(float(sum_income), 2),
            'sum_expense': round(float(sum_expense), 2),
            'balance': round(float(balance), 2),
            'avg_expense': round(float(avg_expense), 2),
            'transactions_count': len(df_filtered),
            'income_count': len(income_df),
            'expense_count': len(expense_df),
            'internal_transfers_excluded': len(df) - len(df_filtered)
        }

        logger.info(f"result_stats {result}")

        return result

    async def get_categories_stat(self, repo: DBRepository,
                                  user_id: BigInteger,
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None
                                  ) -> dict:

        operations: list[Operation] = await repo.get_user_operations(user_id)

        df = self._filter_statistics_date(operations, start_date, end_date)

        if df.empty:
            return {'top_expense_categories': {}, 'top_income_categories': {}}

        df_filtered = self._filter_internal_transfers(df)

        expense_df = df_filtered[~df_filtered['is_income']]

        top_expense_categories = (
            expense_df.groupby('raw_category')['amount']
            .sum()
            .abs()
            .sort_values(ascending=False)
            .head(10)
        )

        income_df = df_filtered[df_filtered['is_income']]

        top_income_categories = (
            income_df.groupby('raw_category')['amount']
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        total_expense = expense_df['amount'].abs().sum()
        total_income = income_df['amount'].sum()

        result_categories = {
            'top_expense_categories': {
                k: {
                    'amount': float(round(v, 2)),
                    'percentage': float(round((v / total_expense) * 100, 2)),
                    'count_operations': len(expense_df[expense_df['raw_category'] == k])
                } for k, v in top_expense_categories.items()
            },
            'top_income_categories': {
                k: {
                    'amount': float(round(v, 2)),
                    'percentage': float(round((v / total_income) * 100, 2)),
                    'count_operations': len(income_df[income_df['raw_category'] == k])
                } for k, v in top_income_categories.items()
            }
        }

        logger.info(f"categories_stat: {result_categories}")

        return result_categories
