import gc
from typing import Any, List

import groundingdino.datasets.transforms as T
import numpy as np
import torch
from core.inference.predictors.label_based_object_detector import (
    LabelBasedDetectedObject,
    LabelBasedObjectDetector,
)
from groundingdino.util.inference import load_image, load_model, predict
from PIL import Image
from typing_extensions import override
from utils.image import convert_normalized_center_to_absolute_corners


class GroundingDinoObjectDetector(LabelBasedObjectDetector):
    def __init__(
        self,
        checkpoint_path: str,
        config_path: str,
        box_threshold: float = 0.35,
        text_threshold: float = 0.25,
    ):
        self.checkpoint_path = checkpoint_path
        self.config_path = config_path
        self.box_threshold = box_threshold
        self.text_threshold = text_threshold
        self.model: Any = None
        self.device = None

    @override
    def load(self, device: str) -> None:
        self.model = (
            load_model(self.config_path, self.checkpoint_path, device=device)
            if self.model is None
            else self.model.to(device)
        )
        self.device = device

    @override
    def unload(self) -> None:
        if self.model is not None:
            try:
                self.model.to("cpu")
            except Exception:
                pass

        self.model = None
        self.device = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.ipc_collect()
            torch.cuda.empty_cache()

    @override
    def detect_with_label(
        self, image: Image.Image, label: str
    ) -> List[LabelBasedDetectedObject]:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() before detection.")

        # Convert PIL Image to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Store original dimensions
        original_width, original_height = image.size

        # Apply the same transform as load_image (expects PIL Image)
        transform = T.Compose(
            [
                T.RandomResize([800], max_size=1333),
                T.ToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
        )

        transformed_image, _ = transform(image, None)

        # Run prediction
        boxes, logits, phrases = predict(
            model=self.model,
            image=transformed_image,
            caption=label,
            box_threshold=self.box_threshold,
            text_threshold=self.text_threshold,
        )

        objects = []
        for box, logit, phrase in zip(boxes, logits, phrases):
            cx, cy, box_w, box_h = box
            bbox = convert_normalized_center_to_absolute_corners(
                cx, cy, box_w, box_h, original_width, original_height
            )
            score = float(logit)

            object = LabelBasedDetectedObject(bbox=bbox, score=score, label=phrase)
            objects.append(object)

        return objects
