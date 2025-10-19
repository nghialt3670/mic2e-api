from typing import List, Optional, Tuple

from chat2edit.execution.decorators import (
    feedback_ignored_return_value,
    feedback_unexpected_error,
)

from core.chat2edit.decorators import feedback_missing_all_optional_parameters
from core.chat2edit.models.box import Box
from core.chat2edit.models.image import Image
from core.chat2edit.models.object import Object
from core.chat2edit.models.point import Point
from core.inference.manager.global_manager import get_predictor_manager
from core.inference.predictors import SamBasedObjectSegmenter, SamBasedSegmentedObject


@feedback_unexpected_error
@feedback_ignored_return_value
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

    object = create_object_from_sam_based_segmented_object(segmented_objects[0])
    image.add_object(object)
    return object


def create_sam_input_parameters(
    box: Optional[Box] = None,
    mask: Optional[Image] = None,
    points: Optional[List[Point]] = None,
) -> Tuple[
    Optional[Tuple[int, int, int, int]],
    Optional[Image.Image],
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
        points
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
    object = Object()
    object.src = segmented_object.mask.tobytes().decode("utf-8")
    object.width = segmented_object.mask.width
    object.height = segmented_object.mask.height
    object.left = segmented_object.bbox[0]
    object.top = segmented_object.bbox[1]
    object.points_to_score[
        segmented_object.positive_points, segmented_object.negative_points
    ] = segmented_object.score
    object.box_to_score[segmented_object.box] = segmented_object.score
    object.mask_to_score[segmented_object.input_mask.tobytes().decode("utf-8")] = (
        segmented_object.score
    )
    return object
