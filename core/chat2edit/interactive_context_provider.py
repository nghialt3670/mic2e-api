from abc import abstractmethod

from chat2edit.base import ContextProvider
from core.predictors import LabelBasedObjectSegmenter, MaskBasedImageInpainter


class InteractiveContextProvider(ContextProvider):
    def __init__(
        self,
        label_based_object_segmenter: LabelBasedObjectSegmenter,
        mask_based_image_inpainter: MaskBasedImageInpainter,
    ):
        self._label_based_object_segmenter = label_based_object_segmenter
        self._mask_based_image_inpainter = mask_based_image_inpainter

    @abstractmethod
    def get_context(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_exemplars(self) -> List[ChatCycle]:
        pass
