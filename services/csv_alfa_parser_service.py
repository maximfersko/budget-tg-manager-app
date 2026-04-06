from datetime import datetime
from typing import Optional, Dict

from services.csv_parser_service import BaseCSVParser


class AlfaBankCSVParser(BaseCSVParser):

    def __init__(self):
        super().__init__(delimiter=',', encoding='utf-8')

    def parse_row(self, row: dict) -> Optional[Dict]:
        status = row.get('status', '')
        if status and status != 'Выполнен':
            return None

        amount = float(row.get('amount'))
        category = row.get('category', 'Без категории')
        operation_type = row.get('type', '')

        raw_date = row.get('operationDate', '')
        try:
            op_date = datetime.strptime(raw_date, "%d.%m.%Y")
        except ValueError:
            try:
                op_date = datetime.strptime(raw_date, "%d.%m.%Y %H:%M:%S")
            except ValueError:
                op_date = datetime.now()

        is_income = operation_type == 'Пополнение'
        
        if is_income:
            amount = abs(amount)
        else:
            amount = -abs(amount)

        return {
            "date": op_date,
            "amount": amount,
            "category": category if category else 'Без категории',
            "description": " ",
            "is_income": is_income
        }
