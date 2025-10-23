import json
from typing import List, Union

from chat2edit.context import Attachment
from fastapi import Body, Depends

from deps.attachment_mapping_service_deps import get_attachment_mapping_service
from schemas import Chat2EditRequestModel
from services import AttachmentMappingService
from utils.files import download_file_to_bytes


def get_attachments(
    request: Chat2EditRequestModel = Body(...),
    attachment_mapping_service: AttachmentMappingService = Depends(
        get_attachment_mapping_service
    ),
) -> List[Attachment]:
    bytess = map(download_file_to_bytes, request.message.attachmentUrls)
    attachments = map(attachment_mapping_service.from_bytes, bytess)
    return list(attachments)
