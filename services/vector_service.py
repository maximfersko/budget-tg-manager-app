import uuid
from datetime import datetime
from typing import List

from core.qdrant_client import qdrant_manager
from core.logger import logger

class VectorService:

    def __init__(self):
        self.client = qdrant_manager.client
        self.collection_name = qdrant_manager.collection_name

    async def save_insight(self, user_id: int, insight_text: str, metadata: dict = None):
        try:
            point_id = str(uuid.uuid4())
            self.client.add(
                collection_name=self.collection_name,
                documents=[insight_text],
                metadata=[{
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    **(metadata or {})
                }],
                ids=[point_id]
            )
            logger.info(f"Insight saved successfully for user {user_id}. ID: {point_id}")
        except Exception as e:
            logger.error(f"Failed to save insight to Qdrant: {e}")

    async def get_relevant_memories(self, user_id: int, query: str, limit: int = 5) -> List[str]:
        try:
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query,
                query_filter={
                    "must": [
                        {"key": "user_id", "match": {"value": user_id}}
                    ]
                },
                limit=limit
            )

            memories = [point.document for point in search_result.points]
            logger.info(f"Retrieved {len(memories)} relevant memories for user {user_id}")
            return memories
        except Exception as e:
            logger.error(f"Failed to search memories in Qdrant: {e}")
            return []
