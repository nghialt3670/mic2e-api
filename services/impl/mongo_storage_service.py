import mimetypes
from typing import Optional
from urllib.parse import quote, unquote, urlparse

from bson.binary import Binary  # type: ignore[import-untyped]
from motor.motor_asyncio import AsyncIOMotorDatabase  # type: ignore[import-untyped]

from services.storage_service import StorageService


class MongoStorageService(StorageService):
    def __init__(
        self,
        database: AsyncIOMotorDatabase,
        bucket: str,
        public_base_url: str,
    ):
        self._collection = database[bucket]
        self._bucket = bucket
        self._public_base_url = public_base_url.rstrip("/")
        # Route prefix is now versionless; external routing/proxy should handle API versioning
        self._route_prefix = f"/storage/{self._bucket}/"

    async def upload(self, data: bytes, path: str) -> str:
        if not path:
            raise ValueError("path is required for MongoStorageService.upload")

        content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"

        await self._collection.update_one(
            {"_id": path},
            {
                "$set": {
                    "data": Binary(data),
                    "content_type": content_type,
                }
            },
            upsert=True,
        )

        # Return relative path instead of full URL
        # Frontend will prepend the API host when displaying
        return f"{self._route_prefix}{quote(path)}"

    async def download(self, url_or_path: str) -> bytes:
        path = self._extract_path(url_or_path)
        document = await self._collection.find_one({"_id": path})
        if not document:
            raise FileNotFoundError(f"File not found for path: {path}")

        return bytes(document["data"])

    def _build_public_url(self, path: str) -> str:
        encoded = quote(path)
        return f"{self._public_base_url}{self._route_prefix}{encoded}"

    def _extract_path(self, url_or_path: str) -> str:
        candidate = url_or_path

        if url_or_path.startswith(("http://", "https://")):
            parsed = urlparse(url_or_path)
            candidate = parsed.path

        if candidate.startswith(self._route_prefix):
            candidate = candidate[len(self._route_prefix) :]
        elif candidate.startswith("/"):
            prefix_index = candidate.find(self._route_prefix)
            if prefix_index != -1:
                candidate = candidate[prefix_index + len(self._route_prefix) :]
            else:
                candidate = candidate.lstrip("/")

        return unquote(candidate)

