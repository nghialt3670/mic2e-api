from typing import Union

from chat2edit.context import Attachment
from pydantic import TypeAdapter

from core.chat2edit.models import Image, Object
from services.attachment_mapping_service import AttachmentMappingService


class FabricAttachmentMappingService(AttachmentMappingService):
    def __init__(self) -> None:
        super().__init__()
        self._type_adapter = TypeAdapter(Union[Image, Object])

    def from_bytes(self, data: bytes) -> Attachment:
        entity = self._type_adapter.validate_json(data)
        if isinstance(entity, Image):
            return Attachment(entity, basename="image")
        elif isinstance(entity, Object):
            return Attachment(entity, basename="object")
        else:
            raise ValueError(f"Unsupported attachment type: {type(entity)}")

    def to_bytes(self, attachment: Attachment) -> bytes:
        return attachment.model_dump()
