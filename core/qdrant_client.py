import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from core.logger import logger

class QdrantManager:
    def __init__(self):
        self.client = QdrantClient(
            host=os.getenv("QDRANT_HOST", "qdrant"),
            port=int(os.getenv("QDRANT_PORT", 6333))
        )
        self.collection_name = "user_memories"
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    # Настройка для совместимости с FastEmbed (имя вектора по умолчанию)
                    vectors_config={
                        "fast-bge-small-en": models.VectorParams(size=384, distance=models.Distance.COSINE)
                    }
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring qdrant collection: {e}")

qdrant_manager = QdrantManager()
