from abc import ABC, abstractmethod
from PIL import Image
from chat2edit.context import Attachment


class AttachmentThumbnailService(ABC):
    @abstractmethod
    def create_thumbnail(self, attachment: Attachment) -> Image.Image:
        pass
