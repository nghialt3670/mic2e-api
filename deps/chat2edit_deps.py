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


logger = logging.getLogger(__name__)
def write_prompt(prompt: LlmMessage) -> None:
    with open(f"logs/prompt_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", "w") as f:
        f.write(prompt.text)

def write_answers(answers: List[LlmMessage]) -> None:
    answer_text = "\n\n".join([answer.text for answer in answers])
    with open(f"logs/answers_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", "w") as f:
        f.write(answer_text)

def write_blocks(blocks: List[ExecutionBlock]) -> None:
    block_text = "\n\n".join([block.model_dump_json(indent=4) for block in blocks])
    with open(f"logs/blocks_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", "w") as f:
        f.write(block_text)

def write_block(block: ExecutionBlock) -> None:
    with open(f"logs/block_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", "w") as f:
        f.write(block.model_dump_json(indent=4))

def get_chat2edit(request: ChatRequestModel = Body(...)) -> Chat2Edit:
    callbacks = Chat2EditCallbacks(
        on_prompt=lambda prompt: write_prompt(prompt),
        on_answers=lambda answers: write_answers(answers),
        on_blocks=lambda blocks: write_blocks(blocks),
        on_execute=lambda block: write_block(block),
    )
    return Chat2Edit(
        llm=_get_llm(request.llm_config),
        context_provider=_get_context_provider(request.language),
        context_strategy=_get_context_strategy(),
        prompting_strategy=_get_prompting_strategy(),
        config=request.chat2edit_config,
        callbacks=callbacks,
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
