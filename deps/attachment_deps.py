import json
from typing import List

from chat2edit.context import Attachment
from fastapi import Body, Depends
from supabase._async.client import AsyncClient

from clients import create_supabase_async_client
from constants import SUPABASE_ATTACHMENT_BUCKET
from schemas import ChatRequestModel
from services import AttachmentMappingService, FileService
from services.impl import FabricAttachmentMappingService, SupabaseFileService
from utils.files import download_file_to_bytes


def get_attachment_mapping_service() -> AttachmentMappingService:
    return FabricAttachmentMappingService()


async def get_attachment_file_service(
    supabase_async_client: AsyncClient = Depends(create_supabase_async_client),
) -> FileService:
    supabase_async_client = await create_supabase_async_client()
    return SupabaseFileService(supabase_async_client, SUPABASE_ATTACHMENT_BUCKET)


def get_attachments(
    request: ChatRequestModel = Body(...),
    attachment_mapping_service: AttachmentMappingService = Depends(
        get_attachment_mapping_service
    ),
) -> List[Attachment]:
    attachment_urls = map(lambda x: x.url, request.message.attachments)
    bytess = map(download_file_to_bytes, attachment_urls)
    filenames = list(map(lambda x: x.original_filename, request.message.attachments))
    attachments = map(lambda x: attachment_mapping_service.from_bytes(x), bytess)
    for i, attachment in enumerate(attachments):
        attachment.__filename__ = filenames[i]

    print(list(attachments))
    return list(attachments)
