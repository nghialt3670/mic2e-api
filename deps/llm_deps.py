import os

from chat2edit.prompting.llms import GoogleLlm, Llm, OpenAILlm
from fastapi import Body

from schemas import ChatRequestModel


def get_llm_from_request(request: ChatRequestModel = Body(...)) -> Llm:
    config = request.llm_config
    if config.provider == "openai":
        llm = OpenAILlm(config.model, **config.params)
        llm.set_api_key(os.getenv("OPENAI_API_KEY"))
        return llm
    elif config.provider == "google":
        llm = GoogleLlm(config.model, **config.params)
        llm.set_api_key(os.getenv("GOOGLE_API_KEY"))
        return llm
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")
