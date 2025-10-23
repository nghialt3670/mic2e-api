import json
from typing import List

from chat2edit.context import Attachment
from fastapi import Body, Depends
from supabase._async.client import AsyncClient

from clients import create_supabase_async_client
from constants import SUPABASE_ATTACHMENTS_BUCKET
from schemas import Chat2EditRequestModel
from services import AttachmentMappingService, FileService
from services.impl import FabricAttachmentMappingService, SupabaseFileService
from utils.files import download_file_to_bytes


def get_attachment_mapping_service() -> AttachmentMappingService:
    return FabricAttachmentMappingService()


async def get_attachment_file_service(
    supabase_async_client: AsyncClient = Depends(create_supabase_async_client),
) -> FileService:
    supabase_async_client = await create_supabase_async_client()
    return SupabaseFileService(supabase_async_client, SUPABASE_ATTACHMENTS_BUCKET)


def get_attachments(
    request: Chat2EditRequestModel = Body(...),
    attachment_mapping_service: AttachmentMappingService = Depends(
        get_attachment_mapping_service
    ),
) -> List[Attachment]:
    bytess = map(download_file_to_bytes, request.message.attachmentUrls)
    attachments = map(attachment_mapping_service.from_bytes, bytess)
    return list(attachments)
