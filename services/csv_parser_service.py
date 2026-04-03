import csv
from abc import abstractmethod
from typing import List, Dict, Optional

from services.parser_service import IParser


class BaseCSVParser(IParser):

    def __init__(self, delimiter: str = ';', encoding: str = 'utf-8'):
        self.delimiter = delimiter
        self.encoding = encoding

    @abstractmethod
    def parse_row(self, row: dict) -> Optional[Dict]:
        pass

    def parse_file(self, file_path: str) -> List[Dict]:
        operations = []
        with open(file_path, mode='r', encoding=self.encoding) as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            for row in reader:
                parsed_operation = self.parse_row(row)
                if parsed_operation:
                    operations.append(parsed_operation)
        return operations
