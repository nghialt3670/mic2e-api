from abc import ABC, abstractmethod
from typing import Any, Dict


class ContextSerializationService(ABC):
    @abstractmethod
    def serialize(self, context: Dict[str, Any]) -> bytes:
        pass

    @abstractmethod
    def deserialize(self, data: bytes) -> Dict[str, Any]:
        pass
