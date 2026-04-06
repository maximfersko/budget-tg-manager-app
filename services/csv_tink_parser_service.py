from datetime import datetime
from typing import Dict, Optional

from services.csv_parser_service import BaseCSVParser


class TinkoffBankCSVParser(BaseCSVParser):

    def __init__(self):
        super().__init__(delimiter=';', encoding='utf-8')

    def parse_row(self, row: dict) -> Optional[Dict]:
        if row.get('Статус') != 'OK':
            return None

        raw_amount = row.get('Сумма операции', '0')
        clean_amount = float(raw_amount.replace(',', '.'))
        
        category = row.get('Категория', 'Без категории')
        description = row.get('Описание', '')

        raw_date = row.get('Дата операции', '')
        try:
            op_date = datetime.strptime(raw_date, "%d.%m.%Y %H:%M:%S")
        except ValueError:
            op_date = datetime.now()

        is_income = clean_amount > 0
        
        if is_income:
            clean_amount = abs(clean_amount)
        else:
            clean_amount = -abs(clean_amount)

        return {
            "date": op_date,
            "amount": clean_amount,
            "category": category,
            "description": description,
            "is_income": is_income
        }
