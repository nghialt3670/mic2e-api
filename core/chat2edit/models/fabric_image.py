from typing import List, Optional

from core.chat2edit.models.fabric_object import FabricObject
from pydantic import Field


class FabricImage(FabricObject):
    """Image object in Fabric.js."""

    type: str = Field(default="Image", description="Object type")

    # Image source
    src: str = Field(default="", description="Image source URL or data")
    crossOrigin: Optional[str] = Field(default=None, description="CORS setting")

    # Image cropping
    cropX: float = Field(default=0, description="Crop X position")
    cropY: float = Field(default=0, description="Crop Y position")

    # Image filters
    filters: List = Field(default_factory=list, description="Image filters")

    # Override default dimensions
    width: float = Field(default=200, description="Image width")
    height: float = Field(default=300, description="Image height")
