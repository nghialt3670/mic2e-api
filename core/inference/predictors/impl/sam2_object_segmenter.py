import gc
import os
from typing import List, Optional, Tuple

import numpy as np
import torch
from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra
from PIL import Image
from sam2.build_sam import build_sam2
from sam2.modeling.sam2_base import SAM2Base
from sam2.sam2_image_predictor import SAM2ImagePredictor
from typing_extensions import override

from core.inference.predictors.box_based_object_segmenter import (
    BoxBasedObjectSegmenter,
    BoxBasedSegmentedObject,
)
from core.inference.predictors.mask_based_object_segmenter import (
    MaskBasedObjectSegmenter,
    MaskBasedSegmentedObject,
)
from core.inference.predictors.point_based_object_segmenter import (
    PointBasedObjectSegmenter,
    PointBasedSegmentedObject,
)
from core.inference.predictors.sam_based_object_segmenter import (
    SamBasedObjectSegmenter,
    SamBasedSegmentedObject,
)
from utils.image import convert_ndarray_to_mask_image, get_bbox_from_mask_image


class Sam2ObjectSegmenter(
    BoxBasedObjectSegmenter,
    MaskBasedObjectSegmenter,
    PointBasedObjectSegmenter,
    SamBasedObjectSegmenter,
):
    def __init__(self, checkpoint_path: str, config_path: str):
        self.checkpoint_path = checkpoint_path
        self.config_path = config_path
        self.model: SAM2Base = None
        self.predictor: SAM2ImagePredictor = None
        self.device = None

    @override
    def load(self, device: str) -> None:
        if self.model is None:
            # Handle config path - SAM2 uses Hydra which expects config dir + name
            config_dir = os.path.dirname(os.path.abspath(self.config_path))
            config_name = os.path.basename(self.config_path).replace(".yaml", "")

            # Clear any existing Hydra instance
            GlobalHydra.instance().clear()

            # Initialize Hydra with the config directory
            initialize_config_dir(config_dir=config_dir, version_base=None)

            try:
                self.model = build_sam2(config_name, self.checkpoint_path, device)
            finally:
                # Clear Hydra instance after building
                GlobalHydra.instance().clear()
        else:
            self.model = self.model.to(device)

        self.predictor = SAM2ImagePredictor(self.model)
        self.device = device

    @override
    def unload(self) -> None:
        if self.model is not None:
            try:
                self.model.to("cpu")
            except Exception:
                pass
        self.device = None
        self.model = None
        self.predictor = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.ipc_collect()
            torch.cuda.empty_cache()

    @override
    def segment_with_box(
        self, image: Image.Image, box: Tuple[int, int, int, int]
    ) -> List[BoxBasedSegmentedObject]:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() before segmentation.")

        self.predictor.set_image(image)
        masks, scores, _ = self.predictor.predict(box=box)

        objects = []
        mask_images, bboxes, scores = self._post_process_result(masks, scores)
        for mask_image, bbox, score in zip(mask_images, bboxes, scores):
            object = BoxBasedSegmentedObject(mask=mask_image, bbox=bbox, score=score)
            objects.append(object)

        return objects

    @override
    def segment_with_points(
        self,
        image: Image.Image,
        positive_points: List[Tuple[int, int]],
        negative_points: List[Tuple[int, int]],
    ) -> List[PointBasedSegmentedObject]:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() before segmentation.")

        point_coords = positive_points + negative_points
        point_labels = [1] * len(positive_points) + [-1] * len(negative_points)
        self.predictor.set_image(image)
        masks, scores, _ = self.predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
        )

        objects = []
        mask_images, bboxes, scores = self._post_process_result(masks, scores)
        for mask_image, bbox, score in zip(mask_images, bboxes, scores):
            object = PointBasedSegmentedObject(mask=mask_image, bbox=bbox, score=score)
            objects.append(object)

        return objects

    @override
    def segment_with_mask(
        self, image: Image.Image, mask: Image.Image
    ) -> List[MaskBasedSegmentedObject]:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() before segmentation.")

        # Convert mask to numpy array for SAM2
        mask_array = np.array(mask)

        # Set image and predict with mask
        self.predictor.set_image(image)
        masks, scores, _ = self.predictor.predict(mask_input=mask_array)

        objects = []
        mask_images, bboxes, scores = self._post_process_result(masks, scores)
        for mask_image, bbox, score in zip(mask_images, bboxes, scores):
            object = MaskBasedSegmentedObject(
                mask=mask_image,
                bbox=bbox,
                score=score,
                input_mask=Image.fromarray(mask_array),
            )
            objects.append(object)

        return objects

    @override
    def segment_with_sam(
        self,
        image: Image.Image,
        box: Optional[Tuple[int, int, int, int]],
        mask: Optional[Image.Image],
        positive_points: Optional[List[Tuple[int, int]]],
        negative_points: Optional[List[Tuple[int, int]]],
    ) -> List[SamBasedSegmentedObject]:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() before segmentation.")

        # Set image
        self.predictor.set_image(image)

        # Prepare prediction parameters
        predict_kwargs = {}

        # Add box if provided
        if box is not None:
            predict_kwargs["box"] = box

        # Add mask if provided
        if mask is not None:
            mask_array = np.array(mask)
            predict_kwargs["mask_input"] = mask_array

        # Add points if provided
        if positive_points is not None or negative_points is not None:
            point_coords = []
            point_labels = []

            if positive_points:
                point_coords.extend(positive_points)
                point_labels.extend([1] * len(positive_points))

            if negative_points:
                point_coords.extend(negative_points)
                point_labels.extend([-1] * len(negative_points))

            if point_coords:
                predict_kwargs["point_coords"] = point_coords
                predict_kwargs["point_labels"] = point_labels

        masks, scores, _ = self.predictor.predict(**predict_kwargs)

        objects = []
        mask_images, bboxes, scores = self._post_process_result(masks, scores)
        for mask_image, bbox, score in zip(mask_images, bboxes, scores):
            object = SamBasedSegmentedObject(
                mask=mask_image,
                bbox=bbox,
                score=score,
                box=box,
                input_mask=mask,
                positive_points=positive_points,
                negative_points=negative_points,
            )
            objects.append(object)

        return objects

    def _post_process_result(
        self, masks: List[np.ndarray], scores: List[float]
    ) -> Tuple[List[Image.Image], List[Tuple[int, int, int, int]], List[float]]:
        mask_images = list(map(convert_ndarray_to_mask_image, masks))
        bboxes = list(map(get_bbox_from_mask_image, mask_images))
        scores = list(map(float, scores))

        return mask_images, bboxes, scores
