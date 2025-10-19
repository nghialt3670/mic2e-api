from copy import deepcopy
from typing import List, Union

from chat2edit.execution.decorators import (
    feedback_ignored_return_value,
    feedback_unexpected_error,
)

from core.chat2edit.decorators import feedback_empty_list_parameters
from core.chat2edit.models.box import Box
from core.chat2edit.models.image import Image
from core.chat2edit.models.object import Object
from core.chat2edit.models.point import Point
from core.chat2edit.models.text import Text
from core.chat2edit.utils import inpaint_uninpainted_objects_in_entities


@feedback_unexpected_error
@feedback_ignored_return_value
@feedback_empty_list_parameters(["entities"])
async def remove_entities(
    image: Image, entities: List[Union[Image, Object, Text, Box, Point]]
) -> Image:
    image = await inpaint_uninpainted_objects_in_entities(image, entities)
    image = image.remove_objects(entities)
    return deepcopy(image)
