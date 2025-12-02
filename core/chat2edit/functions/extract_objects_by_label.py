from typing import List

from chat2edit.execution.decorators import (
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_unexpected_error,
)
from chat2edit.execution.exceptions import FeedbackException
from chat2edit.prompting.stubbing.decorators import exclude_coroutine
from PIL import Image as PILImage

from core.chat2edit.feedbacks import LabelBasedObjectExtractionQuantityMismatchFeedback
from core.chat2edit.models import Image, Object
from core.inference.manager.global_manager import get_predictor_manager
from core.inference.predictors import (
    LabelBasedObjectSegmenter,
    LabelBasedSegmentedObject,
)
from utils.image import convert_image_to_data_url, extract_masked_region


@feedback_ignored_return_value
@feedback_unexpected_error
@feedback_invalid_parameter_type
@exclude_coroutine
async def extract_objects_by_label(
    image: Image, label: str, num_expected_objects: int
) -> List[Object]:
    async with get_predictor_manager().get_predictor(
        LabelBasedObjectSegmenter
    ) as segmenter:
        segmented_objects = segmenter.segment_with_label(image.get_image(), label)

    if len(segmented_objects) != num_expected_objects:
        raise FeedbackException(
            LabelBasedObjectExtractionQuantityMismatchFeedback(
                severity="error",
                label=label,
                num_expected_objects=num_expected_objects,
                num_extracted_objects=len(segmented_objects),
            )
        )

    original_image = image.get_image()
    objects = [
        create_object_from_label_based_segmented_object(obj, original_image)
        for obj in segmented_objects
    ]
    image.add_objects(objects)
    return objects


def create_object_from_label_based_segmented_object(
    segmented_object: LabelBasedSegmentedObject,
    original_image: PILImage.Image,
) -> Object:
    object = Object()
    
    # Extract the masked region from the original image and crop to bounding box
    obj_image = extract_masked_region(
        original_image, segmented_object.mask, segmented_object.bbox
    )
    object.src = convert_image_to_data_url(obj_image)
    
    # Set dimensions from bounding box
    bbox = segmented_object.bbox
    object.width = bbox[2] - bbox[0]
    object.height = bbox[3] - bbox[1]
    object.left = bbox[0]
    object.top = bbox[1]
    object.label_to_score[segmented_object.label] = segmented_object.score
    return object
