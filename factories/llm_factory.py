from typing import Literal

from chat2edit.base import Llm


def create_llm(provider: Literal["openai", "google"]) -> Llm:

    raise ValueError(f"Unsupported LLM provider: {provider}")
