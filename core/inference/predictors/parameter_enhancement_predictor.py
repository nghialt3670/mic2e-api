# core/predictors/image_enhancing_predictor.py
from abc import abstractmethod
from typing import Dict

from PIL import Image

from core.inference.predictors.predictor import Predictor


class ParameterEnhancementPredictor(Predictor):

    @abstractmethod
    def predict_enhancement(self, image: Image.Image) -> Dict[str, float]:
        pass
