from fastapi import Depends
from supabase._async.client import AsyncClient

from clients import create_supabase_async_client
from constants import SUPABASE_ATTACHMENTS_BUCKET, SUPABASE_CONTEXT_BUCKET
from services.file_service import FileService
from services.impl.supabase_file_service import SupabaseFileService


async def get_attachment_file_service(
    supabase_async_client: AsyncClient = Depends(create_supabase_async_client),
) -> FileService:
    supabase_async_client = await create_supabase_async_client()
    return SupabaseFileService(supabase_async_client, SUPABASE_ATTACHMENTS_BUCKET)


async def get_context_file_service(
    supabase_async_client: AsyncClient = Depends(create_supabase_async_client),
) -> FileService:
    supabase_async_client = await create_supabase_async_client()
    return SupabaseFileService(supabase_async_client, SUPABASE_CONTEXT_BUCKET)
