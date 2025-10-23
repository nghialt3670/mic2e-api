from supabase._async.client import AsyncClient
from supabase._sync.client import SyncClient

from clients import create_supabase_async_client, supabase_client


def get_supabase_sync_client() -> SyncClient:
    return supabase_client


async def get_supabase_async_client() -> AsyncClient:
    return await create_supabase_async_client()
