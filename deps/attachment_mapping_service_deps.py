from services.attachment_mapping_service import AttachmentMappingService
from services.impl import FabricAttachmentMappingService


def get_attachment_mapping_service() -> AttachmentMappingService:
    return FabricAttachmentMappingService()
