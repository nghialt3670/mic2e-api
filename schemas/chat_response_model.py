from typing import Optional

from chat2edit.models import ChatCycle
from pydantic import BaseModel, Field

from schemas.message_model import MessageModel


class ChatResponseModel(BaseModel):
    message: Optional[MessageModel] = Field(
        default=None, description="The response message"
    )
    cycle: ChatCycle = Field(description="The new generated chat cycle")
    context_url: str = Field(default="", description="The url of the context")
