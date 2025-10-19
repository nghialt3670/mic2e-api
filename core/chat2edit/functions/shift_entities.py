from copy import deepcopy
from typing import List, Literal, Tuple, Union

from chat2edit.execution.decorators import (
    deepcopy_parameter,
    feedback_ignored_return_value,
)

from core.chat2edit.decorators import (
    feedback_empty_list_parameters,
    feedback_mismatch_list_parameters,
)
from core.chat2edit.models.box import Box
from core.chat2edit.models.image import Image
from core.chat2edit.models.object import Object
from core.chat2edit.models.point import Point
from core.chat2edit.models.text import Text
from core.chat2edit.utils import inpaint_uninpainted_objects_in_entities


@deepcopy_parameter("image")
@feedback_ignored_return_value
@feedback_empty_list_parameters(["entities"])
@feedback_mismatch_list_parameters(["entities", "offsets"])
async def shift_entities(
    image: Image,
    entities: List[Union[Image, Object, Text, Box, Point]],
    offsets: List[Tuple[int, int]],
    unit: Literal["pixel", "percentage"],
) -> Image:
    image_width = image.get_image().width
    image_height = image.get_image().height

    image = await inpaint_uninpainted_objects_in_entities(image, entities)

    for entity, (dx, dy) in zip(entities, offsets):
        if unit == "pixel":
            entity.left = entity.left + dx
            entity.top = entity.top + dy
        elif unit == "percentage":
            dx_pixels = dx * image_width
            dy_pixels = dy * image_height
            entity.left = entity.left + dx_pixels
            entity.top = entity.top + dy_pixels

    return deepcopy(image)
