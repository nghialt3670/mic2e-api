from pydantic import Field

from core.chat2edit.models.fabric.fabric_object import FabricObject


class FabricRect(FabricObject):
    """Rectangle object in Fabric.js."""

    type: str = Field(default="Rect", description="Object type")

    # Rectangle-specific properties
    rx: float = Field(default=0, description="Horizontal border radius")
    ry: float = Field(default=0, description="Vertical border radius")
