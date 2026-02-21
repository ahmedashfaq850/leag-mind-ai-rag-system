from backend.core.config import get_settings
from backend.core.llms.openai_llm import OpenAILLM


def get_llm():
    settings = get_settings()

    if settings.LLM_PROVIDER == "openai":
        return OpenAILLM()

    raise ValueError("Unsupported LLM provider")