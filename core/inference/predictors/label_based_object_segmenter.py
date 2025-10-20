from abc import abstractmethod
from collections import namedtuple
from typing import List

from core.inference.predictors.predictor import Predictor
from PIL import Image

LabelBasedSegmentedObject = namedtuple(
    "LabelBasedSegmentedObject", ["mask", "bbox", "score", "label"]
)


class LabelBasedObjectSegmenter(Predictor):
    @abstractmethod
    def segment_with_label(
        self, image: Image.Image, label: str
    ) -> List[LabelBasedSegmentedObject]:
        pass
