from typing import Any, Dict, List, Union

from chat2edit import Chat2Edit
from chat2edit.context import Attachment
from chat2edit.models import ChatCycle, Message
from fastapi import Body, Depends
from pydantic import TypeAdapter

from core.chat2edit.models import Box, Image, Object, Point, Text
from deps.attachment_deps import get_attachments
from deps.llm_deps import get_llm_from_request
from factories import (
    create_chat2edit,
    create_context_provider,
    create_llm,
    create_prompt_strategy,
)
from schemas import ChatRequestModel
from utils.files import download_file_to_bytes

ContextValue = Union[Image, Object, Box, Point, Text, int, str, float, bool]


def get_chat2edit_from_request(request: ChatRequestModel = Body(...)) -> Chat2Edit:
    return create_chat2edit(
        llm=get_llm_from_request(request),
        context_provider=create_context_provider(request.language),
        strategy=create_prompt_strategy(),
        config=request.chat2edit_config,
    )
