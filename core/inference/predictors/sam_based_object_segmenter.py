from abc import abstractmethod
from collections import namedtuple
from typing import List, Optional, Tuple

from core.inference.predictors.predictor import Predictor
from PIL import Image

SamBasedSegmentedObject = namedtuple(
    "SamBasedSegmentedObject",
    [
        "mask",
        "bbox",
        "score",
        "box",
        "input_mask",
        "positive_points",
        "negative_points",
    ],
)


class SamBasedObjectSegmenter(Predictor):
    @abstractmethod
    def segment_with_sam(
        self,
        image: Image.Image,
        box: Optional[Tuple[int, int, int, int]],
        mask: Optional[Image.Image],
        positive_points: Optional[List[Tuple[int, int]]],
        negative_points: Optional[List[Tuple[int, int]]],
    ) -> List[SamBasedSegmentedObject]:
        pass
