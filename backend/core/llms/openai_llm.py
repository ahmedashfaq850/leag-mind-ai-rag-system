from openai import OpenAI
from backend.core.config import get_settings
from backend.core.llms.base import BaseLLM


class OpenAILLM(BaseLLM):

    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        return response.choices[0].message.content