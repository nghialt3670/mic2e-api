from fastapi import Depends
from supabase._async.client import AsyncClient

from clients import create_supabase_async_client
from constants import SUPABASE_CONTEXT_BUCKET
from services.context_serialization_service import ContextSerializationService
from services.impl.fabric_context_serialization_service import (
    FabricContextSerializationService,
)
from services.impl.supabase_storage_service import SupabaseStorageService
from services.storage_service import StorageService


async def get_context_storage_service(
    client: AsyncClient = Depends(create_supabase_async_client),
) -> StorageService:
    return SupabaseStorageService(client, SUPABASE_CONTEXT_BUCKET)


async def get_context_serialization_service() -> ContextSerializationService:
    return FabricContextSerializationService()
