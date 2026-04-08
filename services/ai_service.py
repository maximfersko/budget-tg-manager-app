import json
from datetime import datetime

import httpx

from core.config import OPENROUTER_API_KEY, LLM_MODEL
from core.logger import logger


class AIService:

    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
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
                content = result['choices'][0]['message']['content']
                return content
        except Exception as e:
            logger.error(f"LLM API Error: {e}")
            return None

    async def parse_user_intent(self, text: str) -> dict:
        current_date = datetime.now().strftime("%Y-%m-%d")
        system_prompt = (
            f"You are a command dispatcher for a financial bot. Today's date is {current_date}. "
            "Your task is to extract the action, date range, and optional category from the user's message (mostly in Russian). "
            "Respond ONLY in JSON format: "
            '{"action": "stats" | "categories" | "unknown", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "category": "string|null"}'
        )

        user_prompt = f"User message: '{text}'"

        response = await self._ask_llm(system_prompt, user_prompt)
        if not response:
            return {"action": "unknown", "start_date": None, "end_date": None, "category": None}

        try:
            logger.info(f"Parsing intent for: {text}")
            clean_res = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_res)
        except Exception as e:
            logger.error(f"Failed to parse AI intent: {e}")
            return {"action": "unknown", "start_date": None, "end_date": None, "category": None}

    async def analyze_spending(self, summary_text: str, user_memories: list = None) -> str:
        memories_str = "\n".join(user_memories) if user_memories else "No previous records."

        system_prompt = (
            "You are a professional financial assistant. "
            "Analyze the provided financial report and context. "
            "Give brief, sharp, and helpful advice. "
            "IMPORTANT: Respond in RUSSIAN. Do NOT use any emojis. Keep it professional."
        )
        
        user_prompt = (
            f"Current Report:\n{summary_text}\n\n"
            f"User context/history:\n{memories_str}\n\n"
            "Analyze this and give advice."
        )

        advice = await self._ask_llm(system_prompt, user_prompt)
        return advice or "Не удалось получить совет от ИИ."

    async def extract_insight(self, summary_text: str) -> str:
        system_prompt = (
            "You are a memory extractor. Analyze the financial report and find ONE key fact about the user's behavior. "
            "The fact should be in the format: 'User usually spends too much on X during weekends' or 'Salary comes every 15th day'. "
            "Respond ONLY with one sentence in English. No emojis."
        )

        insight = await self._ask_llm(system_prompt, f"Report:\n{summary_text}")
        return insight.strip() if insight else None
