import os
from typing import Literal

from chat2edit.prompting.llms import GoogleLlm, Llm, OpenAILlm


def create_llm(provider: Literal["openai", "google"]) -> Llm:
    if provider == "openai":
        llm = OpenAILlm("gpt-3.5-turbo")
        llm.set_api_key(os.getenv("OPENAI_API_KEY"))
        return llm
    elif provider == "google":
        llm = GoogleLlm("gemini-pro")
        llm.set_api_key(os.getenv("GOOGLE_API_KEY"))
        return llm

    raise ValueError(f"Unsupported LLM provider: {provider}")
