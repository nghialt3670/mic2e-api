from fastapi import Depends

from clients import get_mongo_database
from constants import CONTEXT_BUCKET, STORAGE_PUBLIC_BASE_URL
from services.context_serialization_service import ContextSerializationService
from services.impl.fabric_context_serialization_service import (
    FabricContextSerializationService,
)
from services.impl.mongo_storage_service import MongoStorageService
from services.storage_service import StorageService


def get_context_storage_service(
    database=Depends(get_mongo_database),
) -> StorageService:
    return MongoStorageService(database, CONTEXT_BUCKET, STORAGE_PUBLIC_BASE_URL)


async def get_context_serialization_service() -> ContextSerializationService:
    return FabricContextSerializationService()
