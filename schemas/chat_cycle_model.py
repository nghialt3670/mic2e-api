from typing import List, Optional

from chat2edit.models import PromptExecuteLoop
from pydantic import BaseModel

from schemas.message_model import MessageModel


class ChatCycleModel(BaseModel):
    request: MessageModel
    response: Optional[MessageModel]
    loops: List[PromptExecuteLoop]
    context_url: str
