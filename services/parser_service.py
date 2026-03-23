from abc import ABC, abstractmethod
from typing import List, Dict


class IParser(ABC):

    @abstractmethod
    def parse_file(self, file_path: str) -> List[Dict]:
        pass
