import uuid
from datetime import datetime
from typing import List

from qdrant_client.http import models as qmodels

from core.logger import logger
from core.qdrant_client import get_qdrant_client, COLLECTION_NAME


class VectorService:

    @property
    def _client(self):
        return get_qdrant_client()

    async def save_insight(self, user_id: int, insight_text: str, metadata: dict = None):
        try:
            await self._client.add(
                collection_name=COLLECTION_NAME,
                documents=[insight_text],
                metadata=[{
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    **(metadata or {}),
                }],
                ids=[str(uuid.uuid4())],
            )
            logger.info(f"Insight saved for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save insight: {e}")

    async def get_relevant_memories(self, user_id: int, query: str, limit: int = 5) -> List[str]:
        try:
            result = await self._client.query_points(
                collection_name=COLLECTION_NAME,
                query=query,
                query_filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="user_id",
                            match=qmodels.MatchValue(value=user_id),
                        )
                    ]
                ),
                limit=limit,
            )
            memories = [point.document for point in result.points]
            logger.info(f"Retrieved {len(memories)} memories for user {user_id}")
            return memories
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
