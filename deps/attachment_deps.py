from fastapi import Depends
from supabase._async.client import AsyncClient

from clients import create_supabase_async_client
from constants import SUPABASE_ATTACHMENT_BUCKET
from services import (
    AttachmentSerializationService,
    FabricAttachmentSerializationService,
    StorageService,
    SupabaseStorageService,
)


def get_attachment_serialization_service() -> AttachmentSerializationService:
    return FabricAttachmentSerializationService()


async def get_attachment_storage_service(
    client: AsyncClient = Depends(create_supabase_async_client),
) -> StorageService:
    return SupabaseStorageService(client, SUPABASE_ATTACHMENT_BUCKET)
