import re
from typing import Any, Dict, List, Union

from chat2edit.context.attachments import Attachment
from chat2edit.context.strategies import ContextStrategy
from chat2edit.context.utils import path_to_value
from chat2edit.models import (
    ChatMessage,
    ContextualizedFeedback,
    ContextualizedMessage,
    ExecutionFeedback,
)
from chat2edit.utils import SmartTypeAdapter

from core.chat2edit.models import Box, Image, Object, Point, Text

CONTEXT_VALUE_BASE_TYPE = Union[Image, Object, Box, Point, Text, int, str, float, bool]
CONTEXT_TYPE = Dict[str, Union[CONTEXT_VALUE_BASE_TYPE, List[CONTEXT_VALUE_BASE_TYPE]]]


class Mic2eContextStrategy(ContextStrategy):
    def __init__(self) -> None:
        super().__init__()

    def filter_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        filtered_context = {}
        type_adapter = SmartTypeAdapter(CONTEXT_TYPE)
        for k, v in context.items():
            try:
                type_adapter.validate_python(v)
                filtered_context[k] = v
            except Exception as e:
                pass
        return filtered_context

    def contextualize_message(
        self, message: ChatMessage, context: Dict[str, Any]
    ) -> ContextualizedMessage:
        reference_list = re.findall(r"@(\w+)", message.text)
        reference_set = set(reference_list)

        if len(reference_set) != len(reference_list):
            raise ValueError("References must be unique")

        has_references = len(reference_set) > 0
        paths = []

        for attachment in message.attachments:
            if not isinstance(attachment, Image):
                raise ValueError("Attachments must be Image")

            if has_references:
                for obj in attachment.objects:
                    if (
                        not isinstance(obj, (Image, Object, Point, Box, Text))
                        or not obj.reference
                        or obj.reference not in reference_set
                    ):
                        continue

                    if obj.reference in context:
                        raise ValueError(
                            f"Reference {obj.reference} already exists in context"
                        )

                    context[obj.reference] = Attachment(obj)
                    reference_set.remove(obj.reference)
                    paths.append(obj.reference)

                    if obj.is_ephemeral:
                        attachment.remove_object(obj)

            if attachment.reference:
                if attachment.reference in context:
                    raise ValueError(
                        f"Reference {attachment.reference} already exists in context"
                    )

                context[attachment.reference] = Attachment(attachment)
                paths.append(attachment.reference)
            else:
                variable_name = self._get_image_variable_name(context)
                context[variable_name] = Attachment(attachment)
                paths.append(variable_name)

        return ContextualizedMessage(text=message.text, paths=paths)

    def contextualize_feedback(
        self, feedback: ExecutionFeedback, context: Dict[str, Any]
    ) -> ContextualizedFeedback:
        if isinstance(feedback, ContextualizedFeedback):
            return feedback

        raise ValueError(f"Unsupported feedback type: {type(feedback)}")

    def decontextualize_message(
        self, message: ContextualizedMessage, context: Dict[str, Any]
    ) -> ChatMessage:
        return ChatMessage(
            text=message.text,
            attachments=list(map(lambda x: path_to_value(x, context), message.paths)),
        )

    def _get_image_variable_name(self, context: Dict[str, Any]) -> str:
        existing_variable_names = set(context.keys())
        for i in range(1, 100):
            variable_name = f"image_{i}"
            if variable_name not in existing_variable_names:
                return variable_name

        raise RuntimeError("Too many images in context")
