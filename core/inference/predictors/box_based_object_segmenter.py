from abc import abstractmethod
from collections import namedtuple
from typing import List, Tuple

from PIL import Image

from core.inference.predictors.predictor import Predictor

BoxBasedSegmentedObject = namedtuple(
    "BoxBasedSegmentedObject", ["mask", "bbox", "score", "box"]
)


class BoxBasedObjectSegmenter(Predictor):
    @abstractmethod
    def segment_with_box(
        self, image: Image.Image, box: Tuple[int, int, int, int]
    ) -> List[BoxBasedSegmentedObject]:
        pass
