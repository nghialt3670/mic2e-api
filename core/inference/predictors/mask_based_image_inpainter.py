from abc import abstractmethod

from core.inference.predictors.predictor import Predictor
from PIL import Image


class MaskBasedImageInpainter(Predictor):
    @abstractmethod
    def inpaint_with_mask(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        pass
