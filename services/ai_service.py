from core.ai_client import ai_client
from core.logger import logger

class AIService:
    async def analyze_spending(self, summary_text: str, user_memories: list = None):

        context_memories = ""
        if user_memories:
            for m in user_memories:
                date_info = ""
                if m.get('start_date') and m.get('end_date'):
                    s = m['start_date'].split('T')[0]
                    e = m['end_date'].split('T')[0]
                    date_info = f" (за период {s} - {e})"

                context_memories += f"- {m['text']}{date_info}\n"
        else:
            context_memories = "Нет данных из прошлого."
        
        system_prompt = (
            "Ты — профессиональный финансовый ассистент. "
            "Твоя задача — анализировать статистику и давать лаконичные советы. "
            "Используй данные из прошлого, чтобы замечать изменения в поведении."
        )
        
        user_prompt = (
            f"Вот статистика трат за текущий период:\n{summary_text}\n\n"
            f"История инсайтов о пользователе:\n{context_memories}\n\n"
            "Сделай краткий анализ и дай 1-2 совета."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        logger.info("Sending request to AI for analysis with context...")
        return await ai_client.get_completion(messages)

    async def extract_insight(self, summary_text: str):
        system_prompt = (
            "Ты — аналитик. Сформулируй ОДИН короткий факт о финансовом поведении "
            "пользователя для его базы знаний на основе текущей статистики. Одно предложение."
        )
        
        user_prompt = f"Извлеки инсайт из этих данных:\n{summary_text}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return await ai_client.get_completion(messages, temperature=0.3)
