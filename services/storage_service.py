from abc import ABC, abstractmethod
from typing import Any, Dict


class StorageService(ABC):
    @abstractmethod
    async def upload(self, data: bytes, path: str) -> str:
        pass

    @abstractmethod
    async def download(self, url: str) -> bytes:
        pass
