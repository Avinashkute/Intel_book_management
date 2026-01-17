from litellm import acompletion
from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class AIService:
    def __init__(self):
        self.model = settings.LLM_MODEL
        self.temperature = 0.7
        self.max_tokens = 500

    async def _generate(self, prompt: str) -> str:
        try:
            response = await acompletion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API error: {str(e)}")
            raise Exception(f"Failed to generate summary: {str(e)}")

    async def generate_book_summary(self, title: str, author: str, genre: str, year: str) -> str:
        prompt = f"""Generate a concise book summary (1-2 sentences) for:
            Title: {title}
            Author: {author}
            Genre: {genre}
            Year Published: {year}

            Provide only the summary without any additional text."""
        return await self._generate(prompt)

    async def generate_review_summary(self, reviews: list) -> str:
        if not reviews:
            return "No reviews available."
        
        reviews_text = "\n".join([f"- Rating {r['rating']}/5: {r['review_text']}" for r in reviews])
        prompt = f"""Summarize the following book reviews in 2-3 sentences:

         {reviews_text}

Provide only the summary without any additional text."""
        return await self._generate(prompt)
