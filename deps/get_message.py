from typing import List

from chat2edit.context import Attachment
from chat2edit.models import Message
from fastapi import Body, Depends

from deps.get_attachments import get_attachments
from schemas import Chat2EditRequestModel


def get_message(
    request: Chat2EditRequestModel = Body(...),
    attachments: List[Attachment] = Depends(get_attachments),
) -> Message:
    return Message(text=request.message.text, attachments=attachments)
