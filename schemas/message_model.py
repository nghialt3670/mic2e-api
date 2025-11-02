from typing import List

from pydantic import BaseModel, Field

from schemas.attachment_model import AttachmentModel


class MessageModel(BaseModel):
    text: str = Field(description="The text of the message")
    attachments: List[AttachmentModel] = Field(
        default_factory=list, description="The attachments of the message"
    )
