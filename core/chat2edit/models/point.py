from typing import Literal, Optional

from core.chat2edit.models.fabric.objects import FabricImage
from pydantic import Field


class Point(FabricImage):
    segment_type: Optional[Literal["include", "exclude"]] = Field(
        default=None, description="Segment type"
    )
