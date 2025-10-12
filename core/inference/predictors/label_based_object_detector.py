from abc import abstractmethod
from collections import namedtuple
from typing import List

from core.inference.predictors.predictor import Predictor
from PIL import Image

LabelBasedDetectedObject = namedtuple(
    "LabelBasedDetectedObject", ["bbox", "score", "label"]
)


class LabelBasedObjectDetector(Predictor):
    @abstractmethod
    def detect_with_label(
        self, image: Image.Image, label: str
    ) -> List[LabelBasedDetectedObject]:
        pass
