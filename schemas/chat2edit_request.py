from typing import List, Literal

from chat2edit import Chat2EditConfig
from chat2edit.models import ChatCycle
from pydantic import BaseModel, Field


class UserMessage(BaseModel):
    text: str
    attachmentUrls: List[str]


class LlmConfig(BaseModel):
    provider: Literal["openai", "google"] = Field(
        default="openai", description="The type of the llm"
    )
    model_name: str = Field(description="The model name of the llm")
    max_tokens: int = Field(default=2000, description="The max tokens of the llm")
    temperature: float = Field(default=0.1, description="The temperature of the llm")


DEFAULT_LLM_CONFIG = LlmConfig(
    provider="openai", model_name="gpt-3.5-turbo", max_tokens=2000, temperature=0.1
)


DEFAULT_CHAT2EDIT_CONFIG = Chat2EditConfig(
    max_cycles_per_prompt=15,
    max_loops_per_cycle=4,
    max_prompts_per_loop=2,
)


class Chat2EditRequest(BaseModel):
    chatId: str = Field(description="The id of the chat")
    message: UserMessage = Field(description="The user message")
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
    history: List[ChatCycle] = Field(
        default=[], description="The history of the chat2edit"
    )
