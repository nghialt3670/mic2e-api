from abc import abstractmethod
from collections import namedtuple
from typing import List

from PIL import Image

from core.predictors.predictor import Predictor

LabelBasedSegmentedObject = namedtuple(
    "LabelBasedSegmentedObject", ["mask", "bbox", "score", "label"]
)


class LabelBasedObjectSegmenter(Predictor):
    @abstractmethod
    def segment_with_label(
        self, image: Image.Image, label: str
    ) -> List[LabelBasedSegmentedObject]:
        pass
