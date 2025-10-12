import gc
import os
from typing import List, Tuple

import numpy as np
import torch
from core.inference.predictors.box_based_object_segmenter import (
    BoxBasedObjectSegmenter,
    BoxBasedSegmentedObject,
)
from core.inference.predictors.point_based_object_segmenter import (
    PointBasedObjectSegmenter,
    PointBasedSegmentedObject,
)
from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra
from PIL import Image
from sam2.build_sam import build_sam2
from sam2.modeling.sam2_base import SAM2Base
from sam2.sam2_image_predictor import SAM2ImagePredictor
from typing_extensions import override
from utils.image import convert_ndarray_to_mask_image, get_bbox_from_mask_image


class Sam2ObjectSegmenter(BoxBasedObjectSegmenter, PointBasedObjectSegmenter):
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

    def _post_process_result(
        self, masks: List[np.ndarray], scores: List[float]
    ) -> Tuple[List[Image.Image], List[Tuple[int, int, int, int]], List[float]]:
        mask_images = list(map(convert_ndarray_to_mask_image, masks))
        bboxes = list(map(get_bbox_from_mask_image, mask_images))
        scores = list(map(float, scores))

        return mask_images, bboxes, scores
