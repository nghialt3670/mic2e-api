import io

from supabase._async.client import AsyncClient

from services.file_service import FileService


class SupabaseFileService(FileService):
    def __init__(self, supabase_client: AsyncClient, bucket_name: str):
        self._supabase_client = supabase_client
        self._bucket_name = bucket_name

    async def upload_file_from_path(self, source: str, path: str) -> str:
        with open(source, "rb") as file:
            await self._supabase_client.storage.from_(self._bucket_name).upload(
                path, file
            )
            return await self._supabase_client.storage.from_(
                self._bucket_name
            ).get_public_url(path)

    async def upload_file_from_bytes(self, data: bytes, path: str) -> str:
        await self._supabase_client.storage.from_(self._bucket_name).upload(
            path, data
        )
        return await self._supabase_client.storage.from_(
            self._bucket_name
        ).get_public_url(path)
