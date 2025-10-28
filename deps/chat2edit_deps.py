from typing import Any, Dict, List

from chat2edit import Chat2Edit
from chat2edit.context import Attachment
from chat2edit.models import ChatCycle, Message
from fastapi import Body, Depends

from deps.attachment_deps import get_attachments
from factories import (
    create_chat2edit,
    create_context_provider,
    create_llm,
    create_prompt_strategy,
)
from schemas import Chat2EditRequestModel, ChatCycleModel
from utils.files import download_file_to_bytes
from core.chat2edit.models import Box, Image, Object, Point, Text
from pydantic import TypeAdapter
from typing import Union

ContextValue = Union[Image, Object, Box, Point, Text, int, str, float, bool]

def get_message(
    request: Chat2EditRequestModel = Body(...),
    attachments: List[Attachment] = Depends(get_attachments),
) -> Message:
    return Message(text=request.message.text, attachments=attachments)


def get_chat2edit(request: Chat2EditRequestModel = Body(...)) -> Chat2Edit:
    cycles = list(map(_create_chat_cycle_from_model, request.history))
    
    if (cycles):
        last_cycle = cycles[-1]
        context_url = last_cycle.context_url
        context_bytes = download_file_to_bytes(context_url)
        context_type = Dict[str, Union[ContextValue, List[ContextValue]]]
        context_type_adapter = TypeAdapter(context_type)
        context = context_type_adapter.validate_json(context_bytes)
        last_cycle.context = context
        
    return create_chat2edit(
        cycles=cycles,
        llm=create_llm(request.llm_config.provider),
        provider=create_context_provider(request.language),
        strategy=create_prompt_strategy(),
        config=request.chat2edit_config,
    )

def _create_chat_cycle_from_model(model: ChatCycleModel) -> ChatCycle:
    return TypeAdapter(ChatCycle).validate_json(model.model_dump())
