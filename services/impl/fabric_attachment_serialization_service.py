from typing import Union

from chat2edit.context.attachments import Attachment
from pydantic import TypeAdapter

from core.chat2edit.models import Image, Object
from services.attachment_serialization_service import AttachmentSerializationService


class FabricAttachmentSerializationService(AttachmentSerializationService):
    def __init__(self) -> None:
        super().__init__()
        self._type_adapter = TypeAdapter(Union[Image, Object])

    def serialize(self, attachment: Attachment) -> bytes:
        return self._type_adapter.model_dump_json(attachment).encode("utf-8")

    def deserialize(self, data: bytes) -> Attachment:
        entity = self._type_adapter.validate_json(data)
        if isinstance(entity, Image):
            return Attachment(entity, basename="image")
        elif isinstance(entity, Object):
            return Attachment(entity, basename="object")
        else:
            raise ValueError(f"Unsupported attachment type: {type(entity)}")
