import json
from typing import List, Union

from chat2edit.context import Attachment
from fastapi import Body
from PIL import Image as PILImage

from core.chat2edit.models import Image, Object
from schemas.chat2edit_request import Chat2EditRequest
from utils.files import download_file_to_bytes


def get_attachments(request: Chat2EditRequest = Body(...)) -> List[Attachment]:
    bytess = map(download_file_to_bytes, request.message.attachmentUrls)
    entities = map(_create_entity_from_bytes, bytess)
    attachments = map(_create_attachment_from_entity, entities)
    return list(attachments)


def _create_entity_from_bytes(bytes: bytes) -> Image:
    fabric_object = json.loads(bytes)
    fabric_type = fabric_object["type"]

    if fabric_type == "image":
        return Image.model_validate_json(fabric_object)
    elif fabric_type == "object":
        return Object.model_validate_json(fabric_object)
    else:
        raise ValueError(f"Unsupported fabric type: {fabric_type}")


def _create_attachment_from_entity(entity: Union[Image, Object]) -> Attachment:
    if isinstance(entity, Image):
        return Attachment(entity, basename="image")
    elif isinstance(entity, Object):
        return Attachment(entity, basename="object")
    else:
        raise ValueError(f"Unsupported attachment type: {type(entity)}")
