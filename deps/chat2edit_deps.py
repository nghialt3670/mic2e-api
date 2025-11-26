import logging
import os
from datetime import datetime
from typing import List, Union

from chat2edit import Chat2Edit, Chat2EditCallbacks
from chat2edit.context.providers import ContextProvider
from chat2edit.context.strategies import ContextStrategy
from chat2edit.models import ExecutionBlock, LlmMessage
from chat2edit.prompting.llms import GoogleLlm, Llm, OpenAILlm
from chat2edit.prompting.strategies import PromptingStrategy
from fastapi import Body

from core.chat2edit.models import Box, Image, Object, Point, Text
from core.chat2edit.providers import Mic2eContextProvider
from core.chat2edit.strategies import Mic2eContextStrategy, Mic2ePromptingStrategy
from schemas import ChatRequestModel, LlmConfig

ContextValue = Union[Image, Object, Box, Point, Text, int, str, float, bool]


def get_chat2edit(request: ChatRequestModel = Body(...)) -> Chat2Edit:
    return Chat2Edit(
        llm=_get_llm(request.llm_config),
        context_provider=_get_context_provider(request.language),
        context_strategy=_get_context_strategy(),
        prompting_strategy=_get_prompting_strategy(),
        config=request.chat2edit_config,
    )


def _get_llm(config: LlmConfig) -> Llm:
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


def _get_context_provider(language: str) -> ContextProvider:
    return Mic2eContextProvider(language)


def _get_context_strategy() -> ContextStrategy:
    return Mic2eContextStrategy()


def _get_prompting_strategy() -> PromptingStrategy:
    return Mic2ePromptingStrategy()
