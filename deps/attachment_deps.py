from fastapi import Depends

from clients import get_mongo_database
from constants import ATTACHMENT_BUCKET, STORAGE_PUBLIC_BASE_URL
from services import (
    AttachmentSerializationService,
    FabricAttachmentSerializationService,
    MongoStorageService,
    StorageService,
)


def get_attachment_serialization_service() -> AttachmentSerializationService:
    return FabricAttachmentSerializationService()


def get_attachment_storage_service(
    database=Depends(get_mongo_database),
) -> StorageService:
    return MongoStorageService(database, ATTACHMENT_BUCKET, STORAGE_PUBLIC_BASE_URL)
