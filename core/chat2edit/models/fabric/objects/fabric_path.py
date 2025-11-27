from typing import List, Literal, Union

from pydantic import Field

from core.chat2edit.models.fabric.objects.fabric_object import FabricObject


class FabricPath(FabricObject):
    """Path object in Fabric.js (used for scribbles and custom paths)."""

    type: Literal["Path"] = Field(default="Path", description="Object type")

    # Path-specific properties
    # Path commands: each command is a list where first element is the command type
    # (e.g., "M", "L", "Q") followed by numeric coordinates
    # Examples:
    #   ["M", x, y] - Move to point
    #   ["L", x, y] - Line to point
    #   ["Q", x1, y1, x2, y2] - Quadratic curve to point
    path: List[List[Union[str, float]]] = Field(
        default_factory=list, description="Path commands"
    )

