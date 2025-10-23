from typing import Literal

from chat2edit.base import ContextProvider

from core.chat2edit.multimodal_interactive_image_editing_context_provider import (
    MultimodalInteractiveImageEditingContextProvider,
)


def create_context_provider(language: Literal["en", "vi"]) -> ContextProvider:
    return MultimodalInteractiveImageEditingContextProvider(language)
