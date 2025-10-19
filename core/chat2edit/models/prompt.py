from pydantic import Field

from core.chat2edit.models.fabric import FabricObject


class Prompt:
    comment: str = Field(default="", description="Comment of the prompt")
