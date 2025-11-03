from typing import Any, Dict, List, Literal, Optional

from chat2edit import Chat2EditConfig
from chat2edit.models import ChatCycle
from pydantic import BaseModel, Field

from schemas.message_model import MessageModel


class LlmConfig(BaseModel):
    provider: Literal["openai", "google"] = Field(
        default="openai", description="The type of the llm"
    )
    model: str = Field(description="The model name of the llm")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="The parameters of the llm"
    )


DEFAULT_LLM_CONFIG = LlmConfig(provider="openai", model="gpt-3.5-turbo", params={})


DEFAULT_CHAT2EDIT_CONFIG = Chat2EditConfig(
    max_prompt_cycles=5,
    max_llm_exchanges=2,
)


class ChatRequestModel(BaseModel):
    language: Literal["en", "vi"] = Field(
        default="en", description="The language of the user message"
    )
    llm_config: LlmConfig = Field(
        default=DEFAULT_LLM_CONFIG, description="The configuration of the llm"
    )
    chat2edit_config: Chat2EditConfig = Field(
        default=DEFAULT_CHAT2EDIT_CONFIG,
        description="The configuration of the chat2edit",
    )
    message: MessageModel = Field(description="The user message")
    history: List[ChatCycle] = Field(
        default=[], description="The history of the chat2edit"
    )
    context_url: Optional[str] = Field(
        default=None, description="The url of the context"
    )
