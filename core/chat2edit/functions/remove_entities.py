from typing import List, Union

from chat2edit.execution.exceptions import FeedbackException

from core.chat2edit.decorators import feedback_empty_list_parameters
from core.chat2edit.feedbacks import EmptyEntityListFeedback
from core.chat2edit.models.box import Box
from core.chat2edit.models.image import Image
from core.chat2edit.models.object import Object
from core.chat2edit.models.point import Point
from core.chat2edit.models.text import Text
from core.chat2edit.utils import inpaint_uninpainted_objects_in_entities


@feedback_empty_list_parameters(["entities"])
async def remove_entities(
    image: Image, entities: List[Union[Image, Object, Text, Box, Point]]
) -> Image:
    image = await inpaint_uninpainted_objects_in_entities(image, entities)
    image = image.remove_objects(entities)
    return image
