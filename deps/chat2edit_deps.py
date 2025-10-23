from typing import List

from chat2edit import Chat2Edit
from chat2edit.context import Attachment
from chat2edit.models import Message
from fastapi import Body, Depends

from deps.attachment_deps import get_attachments
from factories import (create_chat2edit, create_context_provider, create_llm,
                       create_prompt_strategy)
from schemas import Chat2EditRequestModel


def get_message(
    request: Chat2EditRequestModel = Body(...),
    attachments: List[Attachment] = Depends(get_attachments),
) -> Message:
    return Message(text=request.message.text, attachments=attachments)


def get_chat2edit(request: Chat2EditRequestModel = Body(...)) -> Chat2Edit:
    return create_chat2edit(
        cycles=request.history,
        llm=create_llm(request.llm_config.provider),
        provider=create_context_provider(request.language),
        strategy=create_prompt_strategy(),
        config=request.chat2edit_config,
    )
