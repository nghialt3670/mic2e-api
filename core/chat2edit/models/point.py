from typing import Literal, Optional

from pydantic import Field

from core.chat2edit.models.fabric import FabricImage
from core.chat2edit.models.prompt import Prompt


class Point(FabricImage, Prompt):
    segment_type: Optional[Literal["include", "exclude"]] = Field(
        default=None, description="Segment type"
    )
