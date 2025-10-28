from typing import List

from pydantic import BaseModel

from schemas.attachment_model import AttachmentModel


class MessageModel(BaseModel):
    text: str
    attachments: List[AttachmentModel]
