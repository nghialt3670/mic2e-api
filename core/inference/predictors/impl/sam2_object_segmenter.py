import gc
import os
from typing import List, Optional, Tuple

import numpy as np
import torch
from hydra import initialize_config_dir
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

    def _convert_mask_to_points(
        self, 
        mask: Image.Image, 
        num_points: int = 20,
        sample_negative: bool = False
    ) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Convert a mask to point prompts for SAM2.
        
        For full masks (not scribbles), this samples multiple points from the mask area
        to provide strong guidance to SAM2 about the object location.
        
        Args:
            mask: Binary mask image where non-zero values indicate the object
            num_points: Number of positive points to sample from the mask
            sample_negative: Whether to sample negative points from background
            
        Returns:
            Tuple of (positive_points, negative_points)
        """
        mask_array = np.array(mask)
        
        # Ensure mask is 2D (grayscale)
        if len(mask_array.shape) == 3:
            mask_array = mask_array[:, :, 0] if mask_array.shape[2] > 0 else mask_array.mean(axis=2)
        
        # Get coordinates where mask is non-zero (foreground)
        foreground_coords = np.argwhere(mask_array > 127)  # threshold at 127
        
        positive_points = []
        negative_points = []
        
        if len(foreground_coords) > 0:
            # Sample positive points from foreground
            if len(foreground_coords) > num_points:
                # Use stratified sampling for better coverage
                # Sample points from different regions of the mask
                indices = np.random.choice(len(foreground_coords), num_points, replace=False)
                sampled_coords = foreground_coords[indices]
            else:
                sampled_coords = foreground_coords
            
            # Convert from (y, x) to (x, y) format
            positive_points = [(int(x), int(y)) for y, x in sampled_coords]
            
            # Sample negative points from background if requested
            if sample_negative:
                background_coords = np.argwhere(mask_array <= 127)
                if len(background_coords) > 0:
                    # Sample fewer negative points
                    num_neg = min(num_points // 2, len(background_coords))
                    if num_neg > 0:
                        neg_indices = np.random.choice(len(background_coords), num_neg, replace=False)
                        sampled_neg_coords = background_coords[neg_indices]
                        negative_points = [(int(x), int(y)) for y, x in sampled_neg_coords]
        
        return positive_points, negative_points

    @override
    def segment_with_box(
        self, image: Image.Image, box: Tuple[int, int, int, int]
    ) -> List[BoxBasedSegmentedObject]:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() before segmentation.")

        self.predictor.set_image(image)
        masks, scores, _ = self.predictor.predict(box=np.array(box))

        objects = []
        mask_images, bboxes, scores = self._post_process_result(masks, scores)
        for mask_image, bbox, score in zip(mask_images, bboxes, scores):
            object = BoxBasedSegmentedObject(mask=mask_image, bbox=bbox, score=score, box=box)
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
        point_labels = [1] * len(positive_points) + [0] * len(negative_points)
        
        self.predictor.set_image(image)
        masks, scores, _ = self.predictor.predict(
            point_coords=np.array(point_coords),
            point_labels=np.array(point_labels),
        )

        objects = []
        mask_images, bboxes, scores = self._post_process_result(masks, scores)
        for mask_image, bbox, score in zip(mask_images, bboxes, scores):
            object = PointBasedSegmentedObject(
                mask=mask_image, 
                bbox=bbox, 
                score=score, 
                positive_points=positive_points, 
                negative_points=negative_points
            )
            objects.append(object)

        return objects

    @override
    def segment_with_mask(
        self, image: Image.Image, mask: Image.Image
    ) -> List[MaskBasedSegmentedObject]:
        """
        Segment using a mask by converting it to point prompts.
        
        The mask is converted to multiple positive point prompts sampled from
        the mask area. This provides SAM2 with strong guidance about where
        the object is located.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() before segmentation.")

        # Convert mask to point prompts (positive points only by default)
        positive_points, negative_points = self._convert_mask_to_points(mask, num_points=20, sample_negative=False)
        
        if not positive_points:
            # No foreground points found, return empty list
            return []

        # Use points to segment
        point_coords = positive_points + negative_points
        point_labels = [1] * len(positive_points) + [0] * len(negative_points)
        
        self.predictor.set_image(image)
        masks, scores, _ = self.predictor.predict(
            point_coords=np.array(point_coords),
            point_labels=np.array(point_labels),
            multimask_output=False,  # Use single mask output for better stability with many points
        )

        objects = []
        mask_images, bboxes, scores = self._post_process_result(masks, scores)
        for mask_image, bbox_result, score in zip(mask_images, bboxes, scores):
            object = MaskBasedSegmentedObject(
                mask=mask_image,
                bbox=bbox_result,
                score=score,
                input_mask=mask,
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
        """
        Segment using SAM with various prompt types.
        
        If a mask is provided, it's converted to positive point prompts sampled
        from the mask area. These points are combined with any explicitly provided
        points and box prompts for comprehensive guidance to SAM2.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() before segmentation.")

        # Set image
        self.predictor.set_image(image)

        # Start with provided points
        all_positive_points = list(positive_points) if positive_points else []
        all_negative_points = list(negative_points) if negative_points else []

        # If mask is provided, convert it to points and combine
        if mask is not None:
            mask_pos_points, mask_neg_points = self._convert_mask_to_points(
                mask, 
                num_points=20, 
                sample_negative=False
            )
            all_positive_points.extend(mask_pos_points)
            all_negative_points.extend(mask_neg_points)

        # Prepare prediction parameters
        predict_kwargs = {}

        # Add box if provided
        if box is not None:
            predict_kwargs["box"] = np.array(box)

        # Add combined points if we have any
        if all_positive_points or all_negative_points:
            point_coords = all_positive_points + all_negative_points
            point_labels = [1] * len(all_positive_points) + [0] * len(all_negative_points)
            predict_kwargs["point_coords"] = np.array(point_coords)
            predict_kwargs["point_labels"] = np.array(point_labels)

        # If still no prompts, return empty list
        if not predict_kwargs:
            return []

        # Use single mask output when we have many points for stability
        use_multimask = len(all_positive_points) < 5
        masks, scores, _ = self.predictor.predict(**predict_kwargs, multimask_output=use_multimask)

        objects = []
        mask_images, bboxes, scores = self._post_process_result(masks, scores)
        for mask_image, bbox_result, score in zip(mask_images, bboxes, scores):
            object = SamBasedSegmentedObject(
                mask=mask_image,
                bbox=bbox_result,
                score=score,
                box=box,
                input_mask=mask,
                positive_points=positive_points,
                negative_points=negative_points,
            )
            objects.append(object)

        return objects

    def _post_process_result(
        self, masks: np.ndarray, scores: np.ndarray
    ) -> Tuple[List[Image.Image], List[Tuple[int, int, int, int]], List[float]]:
        mask_images = list(map(convert_ndarray_to_mask_image, masks))
        bboxes = list(map(get_bbox_from_mask_image, mask_images))
        scores = list(map(float, scores))

        return mask_images, bboxes, scores