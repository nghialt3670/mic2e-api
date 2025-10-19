import base64
from typing import Tuple

import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation


def convert_ndarray_to_mask_image(image: np.ndarray) -> Image.Image:
    if image.ndim == 3:
        image = image.squeeze(0)
    image = (image * 255).astype(np.uint8)
    return Image.fromarray(image)


def get_bbox_from_mask_image(mask_image: Image.Image) -> Tuple[int, int, int, int]:
    mask = np.array(mask_image)
    y, x = np.where(mask)
    return min(x), min(y), max(x), max(y)


def convert_normalized_center_to_absolute_corners(
    cx: float, cy: float, box_w: float, box_h: float, img_w: int, img_h: int
) -> Tuple[int, int, int, int]:
    xmin = int((cx - box_w / 2) * img_w)
    ymin = int((cy - box_h / 2) * img_h)
    xmax = int((cx + box_w / 2) * img_w)
    ymax = int((cy + box_h / 2) * img_h)
    return xmin, ymin, xmax, ymax


def expand_mask_image(mask_image: Image.Image, iterations: int = 10) -> Image.Image:
    mask_array = np.array(mask_image)
    binary_mask = (mask_array > 127).astype(np.uint8)
    expanded_mask = binary_dilation(binary_mask, iterations=iterations).astype(np.uint8)
    expanded_mask = expanded_mask * 255
    return Image.fromarray(expanded_mask)


def convert_image_to_data_url(image: Image.Image) -> str:
    bytes = image.convert("RGBA").tobytes()
    return f"data:image/png;base64,{base64.b64encode(bytes).decode('utf-8')}"