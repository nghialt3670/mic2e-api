from typing import List

from PIL import Image
from typing_extensions import override

from core.inference.predictors.box_based_object_segmenter import BoxBasedObjectSegmenter
from core.inference.predictors.label_based_object_detector import (
    LabelBasedObjectDetector,
)
from core.inference.predictors.label_based_object_segmenter import (
    LabelBasedObjectSegmenter,
    LabelBasedSegmentedObject,
)


class TwoStageObjectSegmenter(LabelBasedObjectSegmenter):
    def __init__(
        self, detector: LabelBasedObjectDetector, segmenter: BoxBasedObjectSegmenter
    ):
        self.detector = detector
        self.segmenter = segmenter

    @override
    def load(self, device: str) -> None:
        self.detector.load(device)
        self.segmenter.load(device)

    @override
    def unload(self) -> None:
        self.detector.unload()
        self.segmenter.unload()

    @override
    def segment_with_label(
        self, image: Image.Image, label: str
    ) -> List[LabelBasedSegmentedObject]:
        if self.detector is None or self.segmenter is None:
            raise RuntimeError(
                "Detector or segmenter not loaded. Call load() before segmentation."
            )

        segmented_objects = []
        detected_objects = self.detector.detect_with_label(image, label)
        for detected_obj in detected_objects:
            box_segments = self.segmenter.segment_with_box(image, detected_obj.bbox)

            if box_segments:
                best_segment = box_segments[0]

                combined_score = (detected_obj.score + best_segment.score) / 2.0

                segmented_object = LabelBasedSegmentedObject(
                    mask=best_segment.mask,
                    bbox=best_segment.bbox,
                    score=combined_score,
                    label=detected_obj.label,
                )
                segmented_objects.append(segmented_object)

        return segmented_objects
