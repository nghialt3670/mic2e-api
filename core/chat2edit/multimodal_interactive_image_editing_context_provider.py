from typing import Any, Dict, List

from chat2edit.base import ContextProvider
from chat2edit.models import ChatCycle

from core.chat2edit.exemplars.en_exemplars import EN_EXEMPLARS
from core.chat2edit.exemplars.vi_exemplars import VI_EXEMPLARS
from core.chat2edit.functions import (
    apply_filter,
    extract_object_by_sam,
    extract_objects_by_label,
    locate_entities,
    remove_entities,
    respond_to_user,
    shift_entities,
)


class MultimodalInteractiveImageEditingContextProvider(ContextProvider):
    def __init__(self, language: str):
        super().__init__()
        self._language = language

    def get_context(self) -> Dict[str, Any]:
        return {
            "apply_filter": apply_filter,
            "extract_object_by_sam": extract_object_by_sam,
            "extract_objects_by_label": extract_objects_by_label,
            "locate_entities": locate_entities,
            "remove_entities": remove_entities,
            "shift_entities": shift_entities,
            "respond_to_user": respond_to_user,
        }

    def get_exemplars(self) -> List[ChatCycle]:
        if self._language == "en":
            return EN_EXEMPLARS
        elif self._language == "vi":
            return VI_EXEMPLARS
        else:
            raise ValueError(f"Unsupported language: {self._language}")
