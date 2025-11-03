from abc import ABC, abstractmethod


class StorageService(ABC):
    @abstractmethod
    async def upload(self, data: bytes, path: str) -> str:
        pass

    @abstractmethod
    async def download(self, url: str) -> bytes:
        pass
