import hashlib


class FileService:

    async def calculate_hash(self, file_path: str) -> str:
        f_hash = hashlib.sha256()

        with open(file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                normalized_line = line.rstrip('\r\n') + '\n'
                f_hash.update(normalized_line.encode('utf-8'))

            return f_hash.hexdigest()
