from datetime import datetime
from typing import Any
from chat2edit.context.attachments import Attachment
from pydantic import TypeAdapter

from core.chat2edit.models import Image
from services.attachment_serialization_service import AttachmentSerializationService


class FabricAttachmentSerializationService(AttachmentSerializationService):
    def __init__(self) -> None:
        super().__init__()
        self._type_adapter = TypeAdapter(Image)

    def serialize(self, attachment: Attachment) -> bytes:
        return self._type_adapter.dump_json(attachment.__obj__)    

    def deserialize(self, data: bytes) -> Attachment:
        entity = self._type_adapter.validate_json(data)
        if isinstance(entity, Image):
            return Attachment(entity, basename="image")
        else:
            raise ValueError(f"Unsupported attachment type: {type(entity)}")
