from typing import List

from chat2edit import Chat2Edit, Chat2EditCallbacks, Chat2EditConfig
from chat2edit.base import ContextProvider, PromptStrategy
from chat2edit.models import ChatCycle
from chat2edit.prompting.llms import Llm

CHAT2EDIT_CALLBACKS = Chat2EditCallbacks(
    on_request=lambda message: print(f"Request: {message}"),
    on_prompt=lambda prompt: print(f"Prompt: {prompt}"),
    on_answer=lambda answer: print(f"Answer: {answer}"),
    on_extract=lambda extract: print(f"Extract: {extract}"),
    on_process=lambda process: print(f"Process: {process}"),
    on_execute=lambda execute: print(f"Execute: {execute}"),
    on_feedback=lambda feedback: print(f"Feedback: {feedback}"),
    on_respond=lambda message: print(f"Response: {message}"),
)


def create_chat2edit(
    cycles: List[ChatCycle],
    llm: Llm,
    provider: ContextProvider,
    strategy: PromptStrategy,
    config: Chat2EditConfig,
) -> Chat2Edit:
    return Chat2Edit(
        cycles=cycles,
        llm=llm,
        provider=provider,
        strategy=strategy,
        config=config,
        callbacks=CHAT2EDIT_CALLBACKS,
    )
