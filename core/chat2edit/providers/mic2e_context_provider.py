from typing import Any, Dict, List

from chat2edit.context.providers import ContextProvider
from chat2edit.models import ChatCycle

from core.chat2edit.exemplars import MIC2E_EN_EXEMPLARS, MIC2E_VI_EXEMPLARS
from core.chat2edit.functions.apply_filter import apply_filter
from core.chat2edit.functions.extract_object_by_sam import extract_object_by_sam
from core.chat2edit.functions.extract_objects_by_label import extract_objects_by_label
from core.chat2edit.functions.paste_entities import paste_entities
from core.chat2edit.functions.remove_entities import remove_entities
from core.chat2edit.functions.respond_to_user import respond_to_user
from core.chat2edit.functions.rotate_entities import rotate_entities
from core.chat2edit.functions.shift_entities import shift_entities


class Mic2eContextProvider(ContextProvider):
    def __init__(self, language: str):
        super().__init__()
        self._language = language

    def get_context(self) -> Dict[str, Any]:
        return {
            "apply_filter": apply_filter,
            "extract_object_by_sam": extract_object_by_sam,
            "extract_objects_by_label": extract_objects_by_label,
            "remove_entities": remove_entities,
            "rotate_entities": rotate_entities,
            "paste_entities": paste_entities,
            "shift_entities": shift_entities,
            "respond_to_user": respond_to_user,
        }

    def get_exemplars(self) -> List[ChatCycle]:
        if self._language == "en":
            return MIC2E_EN_EXEMPLARS
        elif self._language == "vi":
            return MIC2E_VI_EXEMPLARS
        else:
            raise ValueError(f"Unsupported language: {self._language}")
