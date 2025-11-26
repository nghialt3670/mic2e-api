from typing import List, Optional, Tuple

from chat2edit.execution.decorators import (
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_missing_all_optional_parameters,
    feedback_unexpected_error,
)
from PIL import Image as PILImage

from core.chat2edit.models import Box, Image, Object, Point
from core.inference.manager.global_manager import get_predictor_manager
from core.inference.predictors import SamBasedObjectSegmenter, SamBasedSegmentedObject
from utils.image import convert_image_to_data_url


@feedback_ignored_return_value
@feedback_unexpected_error
@feedback_invalid_parameter_type
@feedback_missing_all_optional_parameters(["box", "mask", "points"])
async def extract_object_by_sam(
    image: Image,
    box: Optional[Box] = None,
    mask: Optional[Image] = None,
    points: Optional[List[Point]] = None,
) -> Object:
    box_coords, mask_image, positive_points, negative_points = (
        create_sam_input_parameters(box, mask, points)
    )

    async with get_predictor_manager().get_predictor(
        SamBasedObjectSegmenter
    ) as segmenter:
        segmented_objects = segmenter.segment_with_sam(
            image.get_image(),
            box=box_coords,
            mask=mask_image,
            positive_points=positive_points,
            negative_points=negative_points,
        )

    obj = create_object_from_sam_based_segmented_object(segmented_objects[0])
    image.add_object(obj)
    return obj


def create_sam_input_parameters(
    box: Optional[Box] = None,
    mask: Optional[Image] = None,
    points: Optional[List[Point]] = None,
) -> Tuple[
    Optional[Tuple[int, int, int, int]],
    Optional[PILImage.Image],
    Optional[List[Tuple[int, int]]],
    Optional[List[Tuple[int, int]]],
]:
    box_coords = (
        (
            int(box.left),
            int(box.top),
            int(box.left + box.width),
            int(box.top + box.height),
        )
        if box is not None
        else None
    )

    mask_image = mask.get_image() if mask is not None else None

    positive_points, negative_points = create_negative_and_positive_points_from_points(
        points or []
    )

    return box_coords, mask_image, positive_points, negative_points


def create_negative_and_positive_points_from_points(
    points: List[Point],
) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    positive_points = []
    negative_points = []

    for point in points:
        point_coords = (int(point.left), int(point.top))

        if point.segment_type == "include":
            positive_points.append(point_coords)
        elif point.segment_type == "exclude":
            negative_points.append(point_coords)

    return positive_points, negative_points


def create_object_from_sam_based_segmented_object(
    segmented_object: SamBasedSegmentedObject,
) -> Object:
    obj = Object()
    obj.src = convert_image_to_data_url(segmented_object.mask)
    obj.width = segmented_object.mask.width
    obj.height = segmented_object.mask.height
    obj.left = segmented_object.bbox[0]
    obj.top = segmented_object.bbox[1]

    positive_tuple = tuple(segmented_object.positive_points or [])
    negative_tuple = tuple(segmented_object.negative_points or [])

    obj.points_to_score[(positive_tuple, negative_tuple)] = segmented_object.score
    obj.box_to_score[tuple(segmented_object.box)] = segmented_object.score

    if segmented_object.input_mask is not None:
        obj.mask_to_score[
            convert_image_to_data_url(segmented_object.input_mask)
        ] = segmented_object.score

    return obj
