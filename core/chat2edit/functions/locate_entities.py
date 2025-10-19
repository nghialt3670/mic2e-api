from typing import List, Literal, Tuple, Union

from chat2edit.execution.decorators import (
    deepcopy_parameter,
    feedback_ignored_return_value,
    feedback_unexpected_error,
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

PositionName = Literal[
    "center",
    "top",
    "bottom",
    "left",
    "right",
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
]

Location = Union[
    Tuple[float, float],
    PositionName,
]

@deepcopy_parameter("image")
@feedback_unexpected_error
@feedback_ignored_return_value
@feedback_empty_list_parameters(["entities"])
@feedback_mismatch_list_parameters(["entities", "locations"])
async def locate_entities(
    image: Image,
    entities: List[Union[Image, Object, Text, Box, Point]],
    locations: List[Location],
) -> Image:
    image_width = image.get_image().width
    image_height = image.get_image().height

    image = await inpaint_uninpainted_objects_in_entities(image, entities)

    for entity, location in zip(entities, locations):
        if isinstance(location, tuple):
            x, y = location
        else:
            x, y = calculate_position_coordinates(
                location, image_width, image_height, entity.width, entity.height
            )

        entity.left = x
        entity.top = y

    return image


def calculate_position_coordinates(
    position: PositionName,
    image_width: int,
    image_height: int,
    entity_width: float,
    entity_height: float,
) -> tuple[float, float]:
    center_x = (image_width - entity_width) / 2
    center_y = (image_height - entity_height) / 2

    left_x = 0
    right_x = image_width - entity_width
    top_y = 0
    bottom_y = image_height - entity_height

    position_map = {
        "top-left": (left_x, top_y),
        "top": (center_x, top_y),
        "top-right": (right_x, top_y),
        "left": (left_x, center_y),
        "center": (center_x, center_y),
        "right": (right_x, center_y),
        "bottom-left": (left_x, bottom_y),
        "bottom": (center_x, bottom_y),
        "bottom-right": (right_x, bottom_y),
    }

    return position_map[position]
