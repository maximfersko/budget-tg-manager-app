import re
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
        df['date'] = pd.to_datetime(df['date'])
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
            end_date: Optional[datetime] = None,
            categories: Optional[List[str]] = None
    ) -> dict:
        operations: list[Operation] = await repo.get_user_operations(user_id)
        if not operations:
            return {
                'salary': 0, 'sum_income': 0, 'sum_expense': 0, 'balance': 0,
                'avg_expense': 0, 'transactions_count': 0, 'income_count': 0,
                'expense_count': 0, 'internal_transfers_excluded': 0
            }

        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            temp_start = end_date - timedelta(days=30)
            df_check = pd.DataFrame([op.__dict__ for op in operations])
            df_check['date'] = pd.to_datetime(df_check['date'])
            recent_ops = df_check[df_check['date'] >= temp_start]
            if recent_ops.empty:
                last_op_date = df_check['date'].max()
                start_date = last_op_date.replace(day=1, hour=0, minute=0, second=0)
                end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            else:
                start_date = temp_start

        df = self._filter_statistics_date(operations, start_date, end_date)
        
        if categories and not df.empty:
            pattern = '|'.join([re.escape(c) for c in categories])
            df = df[df['raw_category'].str.contains(pattern, case=False, na=False)]

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
        salary = df_filtered[(df_filtered['raw_category'].str.lower() == 'зарплата') & (df_filtered['is_income'] == True)]['amount'].sum()

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
        return result

    async def get_categories_stat(self, repo: DBRepository, user_id: BigInteger, start_date=None, end_date=None) -> dict:
        operations: list[Operation] = await repo.get_user_operations(user_id)
        df = self._filter_statistics_date(operations, start_date or (datetime.now() - timedelta(days=30)), end_date or datetime.now())
        if df.empty: return {'top_expense_categories': {}, 'top_income_categories': {}}
        df_filtered = self._filter_internal_transfers(df)
        expense_df = df_filtered[~df_filtered['is_income']]
        income_df = df_filtered[df_filtered['is_income']]
        total_expense = expense_df['amount'].abs().sum()
        total_income = income_df['amount'].sum()
        top_expense = expense_df.groupby('raw_category')['amount'].sum().abs().sort_values(ascending=False).head(10)
        top_income = income_df.groupby('raw_category')['amount'].sum().sort_values(ascending=False).head(10)
        return {
            'top_expense_categories': {k: {'amount': float(round(v, 2)), 'percentage': float(round((v / total_expense) * 100, 2)) if total_expense > 0 else 0} for k, v in top_expense.items()},
            'top_income_categories': {k: {'amount': float(round(v, 2)), 'percentage': float(round((v / total_income) * 100, 2)) if total_income > 0 else 0} for k, v in top_income.items()}
        }

    def get_summary_for_ai(self, stats: dict, df: pd.DataFrame, is_category_filter: bool = False) -> str:
        if not stats or df.empty: return "No data."
        expense_df = df[df['is_income'] == False]
        top_cats = ", ".join([f"{k}: {v:.0f}" for k, v in expense_df.groupby('raw_category')['amount'].sum().abs().sort_values(ascending=False).head(5).items()]) if not expense_df.empty else "none"
        
        main_report = f"Exp: {stats['sum_expense']:.0f}, Top: {top_cats}"
        if not is_category_filter:
            main_report += f", Bal: {stats['balance']:.0f}, Salary: {stats['salary']:.0f}"
        else:
            main_report += f", Income/Refunds: {stats['sum_income']:.0f}"
            
        return f"Report (Category Filter: {is_category_filter}):\n{main_report}"
