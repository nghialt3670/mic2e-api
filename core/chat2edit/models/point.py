from typing import Literal, Optional

from pydantic import Field

from core.chat2edit.models.fabric.objects import FabricImage


class Point(FabricImage):
    segment_type: Optional[Literal["include", "exclude"]] = Field(
        default=None, description="Segment type"
    )
