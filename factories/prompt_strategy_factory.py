from chat2edit.base import PromptStrategy

from core.chat2edit.multimodal_interactive_image_ediging_prompt_strategy import (
    MultimodalInteractiveImageEditingPromptStrategy,
)


def create_prompt_strategy() -> PromptStrategy:
    return MultimodalInteractiveImageEditingPromptStrategy()
