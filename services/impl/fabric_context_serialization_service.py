from typing import Dict, List, Union

from pydantic import TypeAdapter

from core.chat2edit.models import Box, Image, Object, Point, Scribble, Text
from services.context_serialization_service import ContextSerializationService

ContextBaseValueType = Union[Image, Object, Box, Point, Text, Scribble, int, str, float, bool]
ContextType = Dict[str, Union[ContextBaseValueType, List[ContextBaseValueType]]]


class FabricContextSerializationService(ContextSerializationService):
    def __init__(self) -> None:
        super().__init__()
        self._type_adapter = TypeAdapter(ContextType)

    def serialize(self, context: ContextType) -> bytes:
        return self._type_adapter.dump_json(context)

    def deserialize(self, data: bytes) -> ContextType:
        return self._type_adapter.validate_json(data)
