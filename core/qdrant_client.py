from qdrant_client import QdrantClient
from core.config import QDRANT_HOST, QDRANT_PORT
from qdrant_client.http import models


class QdrantManager:
    def __init__(self):
        self.host = QDRANT_HOST
        self.port = QDRANT_PORT
        self.client = QdrantClient(url=f"http://{self.host}:{self.port}")
        self.collection_name = "user_memories"
        self._init_collection()

    def _init_collection(self):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384, 
                    distance=models.Distance.COSINE
                )
            )

qdrant_manager = QdrantManager()
