from minio import Minio
from minio.error import S3Error

from core.config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET, MINIO_SECURE
from core.logger import logger


class MinIOClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        if self._client is None:
            self._client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_SECURE
            )

            try:
                if not self._client.bucket_exists(MINIO_BUCKET):
                    self._client.make_bucket(MINIO_BUCKET)
                    logger.info(f"MinIO bucket '{MINIO_BUCKET}' created")
                else:
                    logger.info(f"MinIO bucket '{MINIO_BUCKET}' exists")
            except S3Error as e:
                logger.error(f"MinIO error: {e}")
                raise

            logger.info("MinIO connected")
        return self._client

    def get_client(self) -> Minio:
        if self._client is None:
            raise RuntimeError("MinIO not connected. Call connect() first.")
        return self._client


minio_client = MinIOClient()
