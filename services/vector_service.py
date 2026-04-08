import os
from qdrant_client.http import models
from core.qdrant_client import qdrant_manager
from core.logger import logger

class VectorService:
    def __init__(self):
        self.client = qdrant_manager.client
        self.collection_name = qdrant_manager.collection_name

    async def save_insight(self, user_id: int, text: str, metadata: dict = None):
        import uuid
        try:
            self.client.add(
                collection_name=self.collection_name,
                documents=[text],
                metadata=[{"user_id": user_id, **(metadata or {})}],
                ids=[str(uuid.uuid4())]
            )
            logger.info(f"Saved memory for user {user_id}: {text[:50]}...")
        except Exception as e:
            logger.error(f"Failed to save insight: {e}")

    async def get_relevant_memories(self, user_id: int, query: str, limit: int = 5):
        try:
            results = self.client.query(
                collection_name=self.collection_name,
                query_text=query,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=user_id),
                        )
                    ]
                ),
                limit=limit
            )
            
            return [
                {
                    "text": res.document,
                    "start_date": res.metadata.get("start_date"),
                    "end_date": res.metadata.get("end_date")
                } 
                for res in results
            ]
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
