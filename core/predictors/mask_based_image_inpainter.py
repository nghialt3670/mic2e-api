from abc import abstractmethod

from PIL import Image

from core.predictors.predictor import Predictor


class MaskBasedImageInpainter(Predictor):
    @abstractmethod
    def inpaint_with_mask(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        pass
