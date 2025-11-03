from typing import Union

from chat2edit import Chat2Edit
from fastapi import Body

from core.chat2edit.models import Box, Image, Object, Point, Text
from deps.llm_deps import get_llm_from_request
from factories import (
    create_chat2edit,
    create_context_provider,
    create_prompt_strategy,
)
from schemas import ChatRequestModel

ContextValue = Union[Image, Object, Box, Point, Text, int, str, float, bool]


def get_chat2edit_from_request(request: ChatRequestModel = Body(...)) -> Chat2Edit:
    return create_chat2edit(
        llm=get_llm_from_request(request),
        context_provider=create_context_provider(request.language),
        strategy=create_prompt_strategy(),
        config=request.chat2edit_config,
    )
