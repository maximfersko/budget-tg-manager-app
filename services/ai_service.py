import json
import httpx
from datetime import datetime
from core.config import OPENROUTER_API_KEY, LLM_MODEL, OPENROUTER_BASE_URL
from core.logger import logger
from core.prompts import (
    INTENT_PARSER_SYSTEM_PROMPT,
    SPENDING_ANALYSIS_SYSTEM_PROMPT,
    INSIGHT_EXTRACTION_SYSTEM_PROMPT,
    RAG_QUERY_SYSTEM_PROMPT
)

class AIService:

    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = f"{OPENROUTER_BASE_URL}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/maximfersko/budget-tg-manager-app",
            "Content-Type": "application/json"
        }

    async def _ask_llm(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Sending request to LLM ({LLM_MODEL})...")
                response = await client.post(self.base_url, headers=self.headers, json=payload)
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"LLM API Error: {e}")
            return None

    async def parse_user_intent(self, text: str, categories: list = None) -> dict:
        current_date = datetime.now().strftime("%Y-%m-%d")
        cats_str = ", ".join(categories) if categories else "No categories available"
        
        system_prompt = INTENT_PARSER_SYSTEM_PROMPT.format(
            current_date=current_date,
            categories=cats_str
        )
        
        response = await self._ask_llm(system_prompt, f"User message: '{text}'")
        if not response:
            return {"action": "unknown", "start_date": None, "end_date": None, "categories": []}
            
        try:
            clean_res = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_res)
        except Exception as e:
            logger.error(f"Failed to parse AI intent: {e}")
            return {"action": "unknown", "start_date": None, "end_date": None, "categories": []}

    async def analyze_spending(self, summary_text: str, user_memories: list = None) -> str:
        memories_context = ""
        if user_memories and len(user_memories) > 0:
            memories_context = (
                "HISTORICAL CONTEXT (previous insights about user):\n"
                + "\n".join([f"- {mem}" for mem in user_memories])
                + "\n\n"
            )
        
        user_prompt = f"{memories_context}CURRENT REPORT:\n{summary_text}"
        
        advice = await self._ask_llm(SPENDING_ANALYSIS_SYSTEM_PROMPT, user_prompt)
        return advice or "Не удалось получить совет от ИИ."

    async def extract_insight(self, summary_text: str) -> str:
        insight = await self._ask_llm(INSIGHT_EXTRACTION_SYSTEM_PROMPT, f"Report:\n{summary_text}")
        return insight.strip() if insight else None

    async def ask_with_context(self, user_id: int, query: str, vector_service) -> str:

        relevant_memories = await vector_service.get_relevant_memories(user_id, query, limit=5)
        
        context = ""
        if relevant_memories and len(relevant_memories) > 0:
            context = (
                "USER HISTORY CONTEXT:\n"
                + "\n".join([f"- {mem}" for mem in relevant_memories])
                + "\n\n"
            )
        
        user_prompt = f"{context}USER QUESTION:\n{query}"
        
        response = await self._ask_llm(RAG_QUERY_SYSTEM_PROMPT, user_prompt)
        return response or "Не удалось получить ответ от ИИ."
