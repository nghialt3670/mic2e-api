from typing import List, Optional, Tuple

import numpy as np

from chat2edit.execution.decorators import (
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_missing_all_optional_parameters,
    feedback_unexpected_error,
)
from PIL import Image as PILImage, ImageDraw
from chat2edit.prompting.stubbing.decorators import exclude_coroutine
from core.chat2edit.models import Box, Image, Object, Point, Scribble
from core.inference.manager.global_manager import get_predictor_manager
from core.inference.predictors import SamBasedObjectSegmenter, SamBasedSegmentedObject
from utils.image import convert_image_to_data_url, extract_masked_region


@feedback_ignored_return_value
@feedback_unexpected_error
@feedback_invalid_parameter_type
@feedback_missing_all_optional_parameters(["box", "positive_points", "negative_points", "positive_mask", "negative_mask"])
@exclude_coroutine
async def extract_object_by_sam(
    image: Image,
    box: Optional[Box] = None,
    positive_points: Optional[List[Tuple[int, int]]] = None,
    negative_points: Optional[List[Tuple[int, int]]] = None,
    positive_mask: Optional[Scribble] = None,
    negative_mask: Optional[Scribble] = None,
) -> Object:
    box_coords, mask_image, positive_points, negative_points = create_sam_input_parameters(
        box=box,
        positive_points=positive_points,
        negative_points=negative_points,
        positive_mask=positive_mask,
        negative_mask=negative_mask,
        image=image,
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

    obj = create_object_from_sam_based_segmented_object(
        segmented_objects[0], image.get_image()
    )
    image.add_object(obj)
    return obj


def create_sam_input_parameters(
    box: Optional[Box] = None,
    positive_points: Optional[List[Tuple[int, int]]] = None,
    negative_points: Optional[List[Tuple[int, int]]] = None,
    positive_mask: Optional[Scribble] = None,
    negative_mask: Optional[Scribble] = None,
    image: Optional[Image] = None,
) -> Tuple[
    Optional[Tuple[int, int, int, int]],
    Optional[PILImage.Image],
    List[Tuple[int, int]],
    List[Tuple[int, int]],
]:
    box_coords = None
    if box is not None and image is not None:
        # Adjust box coordinates: box uses center of image as origin
        # Need to add image.width/2 to left and image.height/2 to top
        image_pil = image.get_image()
        img_width = image_pil.width
        img_height = image_pil.height
        
        adjusted_left = box.left + img_width / 2
        adjusted_top = box.top + img_height / 2
        
        box_coords = (
            int(adjusted_left),
            int(adjusted_top),
            int(adjusted_left + box.width),
            int(adjusted_top + box.height),
        )

    # We no longer take a neutral mask parameter here; rely solely on
    # positive/negative masks and points.
    mask_image: Optional[PILImage.Image] = None

    # Start from explicitly provided positive/negative points (if any)
    pos = list(positive_points or [])
    neg = list(negative_points or [])

    # Additionally convert positive/negative masks (scribbles) into point prompts
    if positive_mask is not None and image is not None:
        pos_mask_img = convert_scribble_to_mask_image(positive_mask, image)
        pos.extend(_mask_image_to_points(pos_mask_img))

    if negative_mask is not None and image is not None:
        neg_mask_img = convert_scribble_to_mask_image(negative_mask, image)
        neg.extend(_mask_image_to_points(neg_mask_img))

    return box_coords, mask_image, pos, neg


def _mask_image_to_points(mask: PILImage.Image, num_points: int = 20) -> List[Tuple[int, int]]:
    """
    Sample a set of point coordinates from a binary mask image.

    This approximates SAM's behavior of turning masks into point prompts.
    """
    if mask.mode != "L":
        mask = mask.convert("L")
    mask_arr = np.array(mask)
    ys, xs = np.where(mask_arr > 0)
    if xs.size == 0:
        return []

    # Uniformly sample indices across all mask pixels (no randomness for determinism)
    count = min(num_points, xs.size)
    if count <= 0:
        return []
    indices = np.linspace(0, xs.size - 1, count, dtype=int)
    points = [(int(xs[i]), int(ys[i])) for i in indices]
    return points


def convert_scribble_to_mask_image(
    scribble: Scribble, image: Optional[Image] = None
) -> PILImage.Image:
    """Convert a Scribble path to a PIL Image mask."""
    # Get image dimensions
    if image is None:
        raise ValueError("Image is required to convert scribble to mask")
    
    image_pil = image.get_image()
    img_width, img_height = image_pil.size
    
    # Create a blank mask image
    mask = PILImage.new("L", (img_width, img_height), 0)
    draw = ImageDraw.Draw(mask)
    
    # Get scribble path commands
    path_commands = scribble.path
    if not path_commands:
        return mask
    
    # Extract coordinates from path commands
    # Path commands are relative to scribble's position (left, top)
    # Adjust for center-origin: add image.width/2 to left and image.height/2 to top
    scribble_left = int(scribble.left + img_width / 2)
    scribble_top = int(scribble.top + img_height / 2)
    
    # Convert path commands to drawing coordinates
    current_x = scribble_left
    current_y = scribble_top
    points = []
    
    for command in path_commands:
        if not command or len(command) < 2:
            continue
            
        cmd_type = str(command[0]).upper()
        
        if cmd_type == "M":  # Move to
            if len(command) >= 3:
                current_x = scribble_left + float(command[1])
                current_y = scribble_top + float(command[2])
                points = [(current_x, current_y)]
        elif cmd_type == "L":  # Line to
            if len(command) >= 3:
                x = scribble_left + float(command[1])
                y = scribble_top + float(command[2])
                points.append((x, y))
                current_x, current_y = x, y
        elif cmd_type == "Q":  # Quadratic curve
            if len(command) >= 5:
                # Quadratic curve: control point and end point
                cp_x = scribble_left + float(command[1])
                cp_y = scribble_top + float(command[2])
                end_x = scribble_left + float(command[3])
                end_y = scribble_top + float(command[4])
                # Approximate quadratic curve with line segments
                num_segments = 20
                for i in range(num_segments + 1):
                    t = i / num_segments
                    x = (1 - t) ** 2 * current_x + 2 * (1 - t) * t * cp_x + t ** 2 * end_x
                    y = (1 - t) ** 2 * current_y + 2 * (1 - t) * t * cp_y + t ** 2 * end_y
                    points.append((x, y))
                current_x, current_y = end_x, end_y
        elif cmd_type == "Z":  # Close path
            if len(points) > 1:
                points.append(points[0])  # Close the path
    
    # Draw the path on the mask
    if len(points) > 1:
        # Convert to integer coordinates
        int_points = [(int(x), int(y)) for x, y in points]
        # Draw lines with stroke width
        stroke_width = max(1, int(scribble.strokeWidth or 5))
        for i in range(len(int_points) - 1):
            draw.line(
                [int_points[i], int_points[i + 1]],
                fill=255,
                width=stroke_width,
            )
        # Fill the path if it's closed
        if len(int_points) > 2 and int_points[0] == int_points[-1]:
            draw.polygon(int_points, fill=255)
    
    return mask


def create_negative_and_positive_points_from_points(
    points: List[Point],
    image: Optional[Image] = None,
) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    positive_points = []
    negative_points = []

    # Get image dimensions for coordinate adjustment if image is provided
    img_width = 0
    img_height = 0
    if image is not None:
        image_pil = image.get_image()
        img_width = image_pil.width
        img_height = image_pil.height

    for point in points:
        # Adjust point coordinates: points use center of image as origin
        # Need to add image.width/2 to left and image.height/2 to top
        adjusted_left = point.left + img_width / 2
        adjusted_top = point.top + img_height / 2
        point_coords = (int(adjusted_left), int(adjusted_top))

        # Some callers (e.g. notebooks) create Point objects without segment_type.
        # Default those to positive ("include") points to preserve previous behavior.
        segment_type = getattr(point, "segment_type", None) or "include"

        if segment_type == "include":
            positive_points.append(point_coords)
        elif segment_type == "exclude":
            negative_points.append(point_coords)

    return positive_points, negative_points


def create_object_from_sam_based_segmented_object(
    segmented_object: SamBasedSegmentedObject,
    original_image: PILImage.Image,
) -> Object:
    obj = Object()
    
    # Extract the masked region from the original image and crop to bounding box
    obj_image = extract_masked_region(
        original_image, segmented_object.mask, segmented_object.bbox
    )
    obj.src = convert_image_to_data_url(obj_image)
    
    # Set dimensions from bounding box
    bbox = segmented_object.bbox
    obj.width = bbox[2] - bbox[0]
    obj.height = bbox[3] - bbox[1]
    obj.left = bbox[0]
    obj.top = bbox[1]

    positive_tuple = tuple(segmented_object.positive_points or [])
    negative_tuple = tuple(segmented_object.negative_points or [])

    obj.points_to_score[(positive_tuple, negative_tuple)] = segmented_object.score
    
    if segmented_object.box is not None:
        obj.box_to_score[tuple(segmented_object.box)] = segmented_object.score

    if segmented_object.input_mask is not None:
        obj.mask_to_score[
            convert_image_to_data_url(segmented_object.input_mask)
        ] = segmented_object.score

    return obj
