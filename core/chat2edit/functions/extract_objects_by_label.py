from typing import List

from chat2edit.execution.decorators import (
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_unexpected_error,
)
from chat2edit.execution.exceptions import FeedbackException

from core.chat2edit.feedbacks import ObjectExtractionQuantityMismatchFeedback
from core.chat2edit.models import Image, Object
from core.inference.manager.global_manager import get_predictor_manager
from core.inference.predictors import (
    LabelBasedObjectSegmenter,
    LabelBasedSegmentedObject,
)
from utils.image import convert_image_to_data_url


@feedback_ignored_return_value
@feedback_unexpected_error
@feedback_invalid_parameter_type
async def extract_objects_by_label(
    image: Image, label: str, num_expected_objects: int
) -> List[Object]:
    async with get_predictor_manager().get_predictor(
        LabelBasedObjectSegmenter
    ) as segmenter:
        segmented_objects = segmenter.segment_with_label(image.get_image(), label)

    if len(segmented_objects) != num_expected_objects:
        raise FeedbackException(
            ObjectExtractionQuantityMismatchFeedback(
                severity="error",
                num_expected_objects=num_expected_objects,
                num_extracted_objects=len(segmented_objects),
            )
        )

    objects = list(
        map(create_object_from_label_based_segmented_object, segmented_objects)
    )
    image.add_objects(objects)
    return objects


def create_object_from_label_based_segmented_object(
    segmented_object: LabelBasedSegmentedObject,
) -> Object:
    object = Object()
    object.src = convert_image_to_data_url(segmented_object.mask)
    object.width = segmented_object.mask.width
    object.height = segmented_object.mask.height
    object.left = segmented_object.bbox[0]
    object.top = segmented_object.bbox[1]
    object.label_to_score[segmented_object.label] = segmented_object.score
    return object
