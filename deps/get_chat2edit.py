from chat2edit import Chat2Edit
from fastapi import Body

from factories import (
    create_chat2edit,
    create_context_provider,
    create_llm,
    create_prompt_strategy,
)
from schemas.chat2edit_request import Chat2EditRequest


def get_chat2edit(request: Chat2EditRequest = Body(...)) -> Chat2Edit:
    return create_chat2edit(
        cycles=request.history,
        llm=create_llm(request.llm_config.provider),
        provider=create_context_provider(request.language),
        strategy=create_prompt_strategy(),
        config=request.chat2edit_config,
    )
