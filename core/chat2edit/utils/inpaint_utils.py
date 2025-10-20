from typing import List, Union

from core.chat2edit.models.box import Box
from core.chat2edit.models.image import Image
from core.chat2edit.models.object import Object
from core.chat2edit.models.point import Point
from core.chat2edit.models.text import Text
from core.inference.manager.global_manager import get_predictor_manager
from core.inference.predictors import MaskBasedImageInpainter
from PIL.Image import Image as PILImage


async def inpaint_objects(image: Image, objects: List[Object]) -> Image:
    """Inpaint objects in the image."""
    predictor_manager = get_predictor_manager()
    composite_mask = create_composite_mask(objects)
    async with predictor_manager.get_predictor(MaskBasedImageInpainter) as inpainter:
        image.set_image(inpainter.inpaint_with_mask(image.get_image(), composite_mask))

    for object in objects:
        object.is_inpainted = True

    return image


async def inpaint_uninpainted_objects_in_entities(
    image: Image, entities: List[Union[Image, Object, Text, Box, Point]]
) -> Image:
    """Inpaint all uninpainted objects from the entities list."""
    objects_to_inpaint = [
        entity
        for entity in entities
        if isinstance(entity, Object) and not entity.is_inpainted
    ]

    if len(objects_to_inpaint) > 0:
        image = await inpaint_objects(image, objects_to_inpaint)

    return image


def create_composite_mask(objects: List[Object]) -> PILImage:
    """Create a composite mask from multiple objects."""
    if not objects:
        raise ValueError("Cannot create mask from empty object list")

    # Use the first object's dimensions as base
    mask = PILImage.new("L", (objects[0].width, objects[0].height), 0)
    for object in objects:
        # Convert object mask to PIL Image if needed
        if hasattr(object, "mask"):
            object_mask = object.mask
        else:
            # If object doesn't have mask attribute, create one from src
            if hasattr(object, "src") and object.src:
                object_mask = PILImage.frombytes(
                    "L", (object.width, object.height), object.src.encode("utf-8")
                )
            else:
                continue

        mask.paste(object_mask, (int(object.left), int(object.top)))
    return mask
