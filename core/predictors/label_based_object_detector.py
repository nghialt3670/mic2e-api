from abc import abstractmethod
from collections import namedtuple
from typing import List

from PIL import Image

from core.predictors.predictor import Predictor

LabelBasedDetectedObject = namedtuple(
    "LabelBasedDetectedObject", ["bbox", "score", "label"]
)


class LabelBasedObjectDetector(Predictor):
    @abstractmethod
    def detect_with_label(
        self, image: Image.Image, label: str
    ) -> List[LabelBasedDetectedObject]:
        pass
