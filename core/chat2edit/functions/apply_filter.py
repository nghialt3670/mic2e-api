from typing import List, Literal, Optional, Union

from chat2edit.execution.decorators import (
    feedback_ignored_return_value,
    feedback_unexpected_error,
)

from core.chat2edit.decorators import feedback_empty_list_parameters
from core.chat2edit.models.box import Box
from core.chat2edit.models.fabric.filters import (
    BlackWhiteFilter,
    BlurFilter,
    BrightnessFilter,
    ContrastFilter,
    InvertFilter,
    SaturationFilter,
)
from core.chat2edit.models.image import Image
from core.chat2edit.models.object import Object
from core.chat2edit.models.point import Point
from core.chat2edit.models.text import Text


@feedback_unexpected_error
@feedback_ignored_return_value
@feedback_empty_list_parameters(["entities"])
async def apply_filter(
    image: Image,
    entities: List[Union[Image, Object, Text, Box, Point]],
    filter_name: Literal[
        "blackWhite", "blur", "brightness", "contrast", "invert", "saturation"
    ],
    filter_value: Optional[float] = None,
) -> Image:
    filter_obj = None

    if filter_name == "blackWhite":
        filter_obj = BlackWhiteFilter()
    elif filter_name == "blur":
        blur_value = filter_value if filter_value is not None else 0
        filter_obj = BlurFilter(blur=blur_value)
    elif filter_name == "brightness":
        brightness_value = filter_value if filter_value is not None else 0
        filter_obj = BrightnessFilter(brightness=brightness_value)
    elif filter_name == "contrast":
        contrast_value = filter_value if filter_value is not None else 0
        filter_obj = ContrastFilter(contrast=contrast_value)
    elif filter_name == "invert":
        filter_obj = InvertFilter()
    elif filter_name == "saturation":
        saturation_value = filter_value if filter_value is not None else 0
        filter_obj = SaturationFilter(saturation=saturation_value)

    # Apply filter to entities that support it (Image and Object)
    for entity in entities:
        if isinstance(entity, Image):
            entity.apply_filter(filter_obj)
        elif isinstance(entity, Object):
            entity.filters.append(filter_obj)

    return image
