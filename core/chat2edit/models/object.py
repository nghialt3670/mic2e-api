from typing import Dict, List, Tuple

from PIL import Image
from pydantic import Field

from core.chat2edit.models.fabric import FabricImage


class Object(FabricImage):
    is_inpainted: bool = Field(
        default=False, description="Whether the object is inpainted"
    )
    label_to_score: Dict[str, float] = Field(
        default_factory=dict, description="Label to score mapping"
    )
    box_to_score: Dict[Tuple[int, int, int, int], float] = Field(
        default_factory=dict, description="Box to score mapping"
    )
    mask_to_score: Dict[str, float] = Field(
        default_factory=dict, description="Mask to score mapping"
    )
    points_to_score: Dict[
        Tuple[List[Tuple[int, int]], List[Tuple[int, int]]], float
    ] = Field(default_factory=dict, description="Points to score mapping")
