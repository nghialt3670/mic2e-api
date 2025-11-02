from chat2edit.models import ChatCycle
from pydantic import BaseModel, Field

from schemas.message_model import MessageModel


class ChatResponseModel(BaseModel):
    message: MessageModel = Field(description="The llm message")
    cycle: ChatCycle = Field(description="The new generated chat cycle")
    context_url: str = Field(default="", description="The url of the context")
