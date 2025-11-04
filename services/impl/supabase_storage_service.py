import requests
from supabase._async.client import AsyncClient

from services.storage_service import StorageService


class SupabaseStorageService(StorageService):
    def __init__(self, client: AsyncClient, bucket: str):
        self._proxy = client.storage.from_(bucket)

    async def upload(self, data: bytes, path: str) -> str:
        await self._proxy.upload(path, data)
        return await self._proxy.get_public_url(path)

    async def download(self, url: str) -> bytes:
        return requests.get(url).content
