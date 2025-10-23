from typing import List

from chat2edit.context import Attachment
from chat2edit.models import Message
from fastapi import Body, Depends

from deps.get_attachments import get_attachments
from schemas.chat2edit_request import Chat2EditRequest


def get_message(
    request: Chat2EditRequest = Body(...),
    attachments: List[Attachment] = Depends(get_attachments),
) -> Message:
    return Message(text=request.message.text, attachments=attachments)
