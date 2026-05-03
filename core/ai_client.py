from openai import AsyncOpenAI
from core.config import OPENROUTER_API_KEY, LLM_MODEL, OPENROUTER_BASE_URL

class AIClient:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.model = LLM_MODEL
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def get_completion(self, messages: list, temperature: float = 0.7):
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                extra_headers={
                    "HTTP-Referer": "https://github.com/maximfersko/budget-tg-manager-app",
                    "X-Title": "Budget TG Manager Bot",
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to AI: {str(e)}"

ai_client = AIClient()
