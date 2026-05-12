from datetime import datetime
from typing import Optional, Dict

from services.csv_parser_service import BaseCSVParser


class AlfaBankCSVParser(BaseCSVParser):

    def __init__(self):
        super().__init__(delimiter=',', encoding='utf-8')

    def parse_row(self, row: dict) -> Optional[Dict]:
        status = row.get('status', '')

        if status and status not in ('Выполнен', 'В обработке'):
            return None

        amount_raw = row.get('amount', '0') or '0'
        try:
            amount = float(str(amount_raw).replace(',', '.'))
        except (ValueError, TypeError):
            return None

        category = row.get('category') or 'Без категории'
        operation_type = row.get('type', '') or ''
        merchant = row.get('merchant', '') or ''

        raw_date = row.get('operationDate', '')
        try:
            op_date = datetime.strptime(raw_date, "%d.%m.%Y")
        except ValueError:
            try:
                op_date = datetime.strptime(raw_date, "%d.%m.%Y %H:%M:%S")
            except ValueError:
                return None

        is_income = operation_type == 'Пополнение'

        if is_income:
            amount = abs(amount)
        else:
            amount = -abs(amount)

        return {
            "date": op_date,
            "amount": amount,
            "category": category,
            "description": merchant,
            "is_income": is_income,
        }
