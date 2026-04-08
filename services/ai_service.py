from core.ai_client import ai_client
from core.logger import logger

class AIService:
    async def analyze_spending(self, summary_text: str, user_memories: list = None):
        context_memories = "\n".join([f"- {m}" for m in user_memories]) if user_memories else "Нет данных из прошлого."
        
        system_prompt = (
            "Ты — профессиональный финансовый ассистент. "
            "Твоя задача — анализировать сухие цифры статистики и давать краткие, "
            "полезные и дружелюбные советы. Будь лаконичен. "
            "Если видишь аномалии или перерасход, мягко укажи на это."
        )
        
        user_prompt = (
            f"Вот статистика трат пользователя за текущий период:\n{summary_text}\n\n"
            f"Вот что ты знаешь о его привычках из прошлого:\n{context_memories}\n\n"
            "Сделай краткий анализ и дай 1-2 конкретных совета."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        logger.info("Sending request to OpenRouter for spending analysis...")
        return await ai_client.get_completion(messages)

    async def extract_insight(self, summary_text: str):
        """
        Извлекает из статистики один короткий факт-инсайт для записи в память (Qdrant).
        """
        system_prompt = (
            "Ты — аналитик данных. Твоя задача — прочитать статистику трат "
            "и сформулировать ОДИН короткий факт о финансовом поведении пользователя "
            "для его 'личного дела'. Факт должен быть в одно предложение."
        )
        
        user_prompt = f"Извлеки инсайт из этих данных:\n{summary_text}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return await ai_client.get_completion(messages, temperature=0.3)
