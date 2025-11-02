from typing import Any, Dict, List, Union

from chat2edit.context import Attachment
from pydantic import TypeAdapter

from core.chat2edit.models import Box, Image, Object, Point, Text
from services.context_serialization_service import ContextSerializationService

ContextBaseValueType = Union[Image, Object, Box, Point, Text, int, str, float, bool]
ContextType = Dict[str, Union[ContextBaseValueType, List[ContextBaseValueType]]]


class FabricContextSerializationService(ContextSerializationService):
    def __init__(self) -> None:
        super().__init__()
        self._type_adapter = TypeAdapter(ContextType)

    def serialize(self, context: ContextType) -> bytes:
        return self._type_adapter.dump_json(context)

    def deserialize(self, data: bytes) -> ContextType:
        return self._type_adapter.validate_json(data)
