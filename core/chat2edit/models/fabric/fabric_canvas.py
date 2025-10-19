from typing import Any, Dict, List

from pydantic import BaseModel, Field


class FabricCanvas(BaseModel):
    """Canvas object in Fabric.js that contains all objects."""

    version: str = Field(default="6.7.1", description="Fabric.js version")
    objects: List[Dict[str, Any]] = Field(
        default_factory=list, description="Objects on the canvas"
    )

    class Config:
        extra = "allow"  # Allow additional canvas properties
