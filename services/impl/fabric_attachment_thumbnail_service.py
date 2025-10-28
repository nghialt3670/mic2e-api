from PIL import Image
from services.attachment_thumbnail_service import AttachmentThumbnailService
from chat2edit.context import Attachment

class FabricAttachmentThumbnailService(AttachmentThumbnailService):
    def create_thumbnail(self, attachment: Attachment) -> Image.Image:
        return 