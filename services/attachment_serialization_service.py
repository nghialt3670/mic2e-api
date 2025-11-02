from abc import ABC, abstractmethod

from chat2edit.context.attachments import Attachment


class AttachmentSerializationService(ABC):
    @abstractmethod
    def serialize(self, attachment: Attachment) -> bytes:
        pass

    @abstractmethod
    def deserialize(self, data: bytes) -> Attachment:
        pass
