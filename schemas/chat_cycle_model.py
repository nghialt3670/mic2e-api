from typing import List, Optional

from chat2edit.models import ChatCycle, PromptExecuteLoop

from schemas.message_model import MessageModel


class ChatCycleModel(ChatCycle):
    request: MessageModel
    response: Optional[MessageModel]
    loops: List[PromptExecuteLoop]
    context_url: str
