from abc import ABC, abstractmethod


class FileService(ABC):
    @abstractmethod
    async def upload_file_from_path(self, source: str, path: str) -> str:
        pass

    @abstractmethod
    async def upload_file_from_bytes(self, data: bytes, path: str) -> str:
        pass
