from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from core.config import QDRANT_HOST, QDRANT_PORT

COLLECTION_NAME = "user_memories"
_VECTOR_SIZE = 384

_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(url=f"http://{QDRANT_HOST}:{QDRANT_PORT}")
        _client.set_model("intfloat/multilingual-e5-small")
    return _client


async def ensure_collection() -> None:
    client = get_qdrant_client()
    collections = await client.get_collections()
    if not any(c.name == COLLECTION_NAME for c in collections.collections):
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=_VECTOR_SIZE, distance=models.Distance.COSINE),
        )
