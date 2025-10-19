from abc import abstractmethod
from collections import namedtuple
from typing import List, Tuple

from PIL import Image

from core.inference.predictors.predictor import Predictor

PointBasedSegmentedObject = namedtuple(
    "PointBasedSegmentedObject",
    ["mask", "bbox", "score", "positive_points", "negative_points"],
)


class PointBasedObjectSegmenter(Predictor):
    @abstractmethod
    def segment_with_points(
        self,
        image: Image.Image,
        positive_points: List[Tuple[int, int]],
        negative_points: List[Tuple[int, int]],
    ) -> List[PointBasedSegmentedObject]:
        pass
