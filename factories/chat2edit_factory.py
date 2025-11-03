
from chat2edit import (
    Chat2Edit,
    Chat2EditCallbacks,
    Chat2EditConfig,
    ContextProvider,
    Llm,
    PromptStrategy,
)

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
    llm: Llm,
    conteprovider: ContextProvider,
    strategy: PromptStrategy,
    config: Chat2EditConfig,
) -> Chat2Edit:
    return Chat2Edit(
        llm=llm,
        provider=provider,
        strategy=strategy,
        config=config,
        callbacks=CHAT2EDIT_CALLBACKS,
    )
