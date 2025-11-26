import base64
import io
import re
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
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    png_bytes = buffer.read()
    return f"data:image/png;base64,{base64.b64encode(png_bytes).decode('utf-8')}"


def convert_data_url_to_image(data_url: str) -> Image.Image:
    match = re.search(r"data:image/(.*?);base64,(.*)", data_url)
    if not match:
        raise ValueError("Invalid data URL")

    image_data = base64.b64decode(match.group(2))
    return Image.open(io.BytesIO(image_data))
