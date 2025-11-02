import os
from typing import Literal

from chat2edit.base import Llm
from chat2edit.prompting.llms import GoogleLlm, OpenAILlm


def create_llm(provider: Literal["openai", "google"]) -> Llm:

    raise ValueError(f"Unsupported LLM provider: {provider}")
