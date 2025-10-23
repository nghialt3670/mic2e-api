from abc import ABC, abstractmethod

from chat2edit.context import Attachment


class AttachmentMappingService(ABC):
    @abstractmethod
    def from_bytes(self, data: bytes) -> Attachment:
        pass

    @abstractmethod
    def to_bytes(self, attachment: Attachment) -> bytes:
        pass
