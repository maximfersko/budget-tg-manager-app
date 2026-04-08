import asyncio
import os
from datetime import datetime
from redis.asyncio import Redis

from core.config import MINIO_BUCKET, BOT_TOKEN, REDIS_URL
from core.logger import logger
from database.minio_client import minio_client
from database.repo import DBRepository
from dto.user_dto import UserDto
from services.csv_alfa_parser_service import AlfaBankCSVParser
from services.csv_tink_parser_service import TinkoffBankCSVParser
from services.pdf_sber_parser_service import SberBankPDFParser
from services.file_service import FileService
from workers.tasks.celery_config import celery_app
from workers.tasks.notifications import notify_user_file_processed


@celery_app.task(bind=True, max_retries=3)
def process_file(self, file_id: str, user_info: dict, file_name: str, bank_code: str) -> dict:
    async def _process():
        file_path = None
        redis_cli = None
        bot = None
        
        try:
            from database.engine import get_async_session_maker
            
            worker_session = get_async_session_maker()
            
            user_dto = UserDto(**user_info)
            user_id = user_dto.user_id

            logger.info(f"Processing file {file_name} for user {user_id}, bank: {bank_code}")

            from aiogram import Bot

            bot = Bot(token=BOT_TOKEN)
            
            file_extension = file_name.lower().split('.')[-1]
            file_path = f"/tmp/incomes_{user_id}_{file_id}.{file_extension}"

            file_service = FileService()

            file_info = await bot.get_file(file_id)
            await bot.download_file(file_info.file_path, destination=file_path)
            logger.info(f"File downloaded to {file_path}")
            
            f_hash = file_service.calculate_hash(file_path)
            cache_key = f'file:hash:{f_hash}'

            redis_cli = Redis.from_url(REDIS_URL, decode_responses=True)
            file_exists = await redis_cli.exists(cache_key)
            
            if file_exists:
                raise FileExistsError(f'File {file_name} already uploaded')

            if bank_code == "tinkoff":
                parser = TinkoffBankCSVParser()
            elif bank_code == "alfa":
                parser = AlfaBankCSVParser()
            elif bank_code == "sber":
                parser = SberBankPDFParser()
            else:
                raise ValueError(f"Unsupported bank: {bank_code}")

            operations = parser.parse_file(file_path)
            logger.info(f"Parsed {len(operations)} operations")

            async with worker_session() as session:
                repo = DBRepository(session)

                await repo.add_user(
                    tg_id=user_dto.user_id,
                    first_name=user_dto.first_name,
                    last_name=user_dto.last_name,
                    username=user_dto.username
                )

                result = await repo.add_operations_batch(user_id, operations, bank_code)

            logger.info(f"Saved to DB: {result}")

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            year = datetime.utcnow().year
            month = datetime.utcnow().month
            s3_key = f"uploads/{user_id}/{year}/{month:02d}/{timestamp}_{file_name}"
            
            content_type = "application/pdf" if file_extension == "pdf" else "text/csv"

            minio_cli = minio_client.get_client()
            minio_cli.fput_object(
                bucket_name=MINIO_BUCKET,
                object_name=s3_key,
                file_path=file_path,
                content_type=content_type
            )

            logger.info(f"File uploaded to MinIO: {s3_key}")
            
            await redis_cli.setex(cache_key, 1209600, str(user_id))
            logger.info(f"File hash cached: {cache_key}")

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Temp file removed: {file_path}")

            return {
                "status": "success",
                "added": result['added'],
                "duplicates": result['duplicates'],
                "s3_key": s3_key
            }

        except ValueError as e:
            logger.error(f"Validation error: {e}")
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            return {"status": "failed", "error": str(e)}

        except FileExistsError as e:
            return {"status": "failed", "error": str(e)}

        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)

            if self.request.retries >= self.max_retries:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                logger.error("Max retries reached, giving up")
                return {"status": "failed", "error": str(e)}

            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(exc=e, countdown=countdown)
        
        finally:
            if redis_cli:
                await redis_cli.aclose()
            if bot:
                await bot.session.close()

    try:
        result = asyncio.run(_process())
        logger.info(f"File processing completed: {result}")
        
        user_id = user_info.get("user_id")
        if user_id:
            notify_user_file_processed.delay(user_id=user_id, result=result)
        
        return result

    except Exception as e:
        logger.error(f"Task retry triggered: {e}")
        raise
