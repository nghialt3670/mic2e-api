from abc import abstractmethod
from collections import namedtuple
from typing import List, Tuple

from core.inference.predictors.predictor import Predictor
from PIL import Image

BoxBasedSegmentedObject = namedtuple(
    "BoxBasedSegmentedObject", ["mask", "bbox", "score", "box"]
)


class BoxBasedObjectSegmenter(Predictor):
    @abstractmethod
    def segment_with_box(
        self, image: Image.Image, box: Tuple[int, int, int, int]
    ) -> List[BoxBasedSegmentedObject]:
        pass
