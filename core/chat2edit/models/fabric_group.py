from typing import Any, Dict, List

from core.chat2edit.models.fabric_object import FabricObject
from pydantic import BaseModel, Field


class LayoutManager(BaseModel):
    """Layout manager for group objects."""

    type: str = Field(default="layoutManager", description="Layout manager type")
    strategy: str = Field(default="fit-content", description="Layout strategy")


class FabricGroup(FabricObject):
    """Group object in Fabric.js that contains multiple objects."""

    type: str = Field(default="Group", description="Object type")

    # Group-specific properties
    subTargetCheck: bool = Field(
        default=False, description="Enable sub-target checking"
    )
    interactive: bool = Field(default=False, description="Interactive group")

    # Layout management
    layoutManager: LayoutManager = Field(
        default_factory=LayoutManager, description="Layout manager configuration"
    )

    # Child objects
    objects: List[Dict[str, Any]] = Field(
        default_factory=list, description="Child objects in the group"
    )

    # Override default stroke
    stroke: None = Field(default=None, description="Stroke color")
    strokeWidth: float = Field(default=0, description="Stroke width")
