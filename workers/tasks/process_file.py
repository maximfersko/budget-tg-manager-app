import asyncio
from datetime import datetime

from core.config import MINIO_BUCKET
from database.minio_client import minio_client
from database.models import User
from database.repo import DBRepository
from services.csv_alfa_parser_service import AlfaBankCSVParser
from services.csv_tink_parser_service import TinkoffBankCSVParser
from workers.tasks import celery_app
from core.logger import logger


@celery_app(bind=True, max_retries=3)
def process_file(self, file_path: str, user, file_name: str, bank_code: str) -> dict:
    async def _processing_file():
        logger.info(f'processing file {file_path} from workers')

        minio_cli = minio_client.get_client()
        timestamp = int(datetime.now().timestamp())
        object_name = f"uploads/{tg_id}/{datetime.year}/{datetime.month}/{file_name}_{timestamp}.csv"

        minio_cli.fput_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
            file_path=file_path,
            content_type="text/csv"
        )

        if bank_code == "tinkoff":
            parser = TinkoffBankCSVParser()
        elif bank_code == "alfa":
            parser = AlfaBankCSVParser()
        elif bank_code == "sber":
            pass

        result_csv = parser.parse_file(file_path)

        repository = DBRepository()

        return {
            'status': 'uploaded',
            'file_path': file_path,
        }

    try:
        result = asyncio.run(_processing_file())
        return result
    except ValueError as e:

        logger.error(f"Validation error: {e}")
        return {"status": "failed", "error": str(e)}

    except Exception as e:

        retry_num = self.request.retries + 1
        logger.error(f"Task failed, retry {retry_num}/{self.max_retries}: {e}")

        if self.request.retries >= self.max_retries:
            logger.error("Max retries reached, giving up")
            return {"status": "failed", "error": str(e)}

        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=countdown)
