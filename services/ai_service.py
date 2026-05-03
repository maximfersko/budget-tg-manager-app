import json
import httpx
from datetime import datetime
from core.config import OPENROUTER_API_KEY, LLM_MODEL, OPENROUTER_BASE_URL
from core.logger import logger

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
        
        system_prompt = (
            f"You are a command dispatcher for a financial bot. Today's date is {current_date}.\n"
            f"Available database categories: {cats_str}\n\n"
            "Analyze the user message and extract: action, date range, and a LIST of relevant categories.\n"
            "DATE RANGE RULES:\n"
            "1. If user says 'for a year' ('за год'), 'for a month' ('за месяц'), 'for a week' ('за неделю'), "
            "it means from TODAY back to the past (e.g., today is 2026-04-08, so 'for a year' is 2025-04-08 to 2026-04-08).\n"
            "2. Only use calendar years (like 01.01 to 31.12) if the user explicitly specifies a year (e.g., 'for 2025').\n"
            "3. If no specific period is mentioned, use the last 30 days.\n\n"
            "CATEGORY RULES:\n"
            "Map query to relevant categories from the available list. Support multiple categories.\n"
            "Respond ONLY in JSON:\n"
            '{"action": "stats" | "categories" | "unknown", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "categories": ["string"]}'
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
        memories_str = "\n".join(user_memories) if user_memories else "No previous records."
        system_prompt = (
            "You are a professional financial assistant. Analyze the report and give advice.\n"
            "IMPORTANT: Respond in RUSSIAN. Do NOT use emojis. Professional tone."
        )
        advice = await self._ask_llm(system_prompt, f"Report:\n{summary_text}\n\nHistory:\n{memories_str}")
        return advice or "Не удалось получить совет от ИИ."

    async def extract_insight(self, summary_text: str) -> str:
        system_prompt = "Find ONE key behavioral fact from the report. ONE sentence in English. No emojis."
        insight = await self._ask_llm(system_prompt, f"Report:\n{summary_text}")
        return insight.strip() if insight else None
