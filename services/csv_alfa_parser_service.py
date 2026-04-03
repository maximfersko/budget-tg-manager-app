from datetime import datetime
from typing import Optional, Dict

from services.csv_parser_service import BaseCSVParser


class AlfaBankCSVParser(BaseCSVParser):

    def __init__(self):
        super().__init__(delimiter=',', encoding='utf-8')

    def parse_row(self, row: dict) -> Optional[Dict]:
        if row.get('status') != 'Выполнен':
            return None

        amount = float(row.get('amount'))
        category = row.get('category')

        raw_date = row.get('operationDate', '')
        try:
            op_date = datetime.strptime(raw_date, "%d.%m.%Y %H:%M:%S")
        except ValueError:
            op_date = datetime.now()

        return {
            "date": op_date,
            "amount": amount,
            "category": category,
            "description": " ",
            "is_income": amount > 0
        }
