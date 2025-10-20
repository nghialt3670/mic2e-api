from abc import abstractmethod
from collections import namedtuple
from typing import List, Tuple

from core.inference.predictors.predictor import Predictor
from PIL import Image

MaskBasedSegmentedObject = namedtuple(
    "MaskBasedSegmentedObject", ["mask", "bbox", "score", "input_mask"]
)


class MaskBasedObjectSegmenter(Predictor):
    @abstractmethod
    def segment_with_mask(
        self, image: Image.Image, mask: Image.Image
    ) -> List[MaskBasedSegmentedObject]:
        pass
