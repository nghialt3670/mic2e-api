import os

from supabase import create_async_client, create_client
from supabase._async.client import AsyncClient
from supabase._sync.client import SyncClient

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase_client: SyncClient = create_client(
    url=SUPABASE_URL,
    key=SUPABASE_ANON_KEY,
)


async def create_supabase_async_client() -> AsyncClient:
    return await create_async_client(
        url=SUPABASE_URL,
        key=SUPABASE_ANON_KEY,
    )
