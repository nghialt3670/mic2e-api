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
from pydantic import TypeAdapter

from core.chat2edit.models import Box, Image, Object, Point, Text
from core.chat2edit.models.fabric.objects import FabricRect, FabricText

CONTEXT_VALUE_BASE_TYPE = Union[Image, Object, Box, Point, Text, int, str, float, bool]
CONTEXT_TYPE = Dict[str, Union[CONTEXT_VALUE_BASE_TYPE, List[CONTEXT_VALUE_BASE_TYPE]]]


class Mic2eContextStrategy(ContextStrategy):
    def __init__(self) -> None:
        super().__init__()

    def filter_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        filtered_context = {}
        type_adapter = TypeAdapter(CONTEXT_TYPE)
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

        # -----------------------------
        # 1. Parse NEW format: #color[label](value@figId)
        # -----------------------------
        ref_pattern = r"#([a-zA-Z0-9_]+)\[([^\]]+)\]\(([^@]+)@([^)]+)\)"
        matches = re.findall(ref_pattern, message.text)

        reference_map = {}        # UUID → python-safe variable_name
        reference_objects = {}    # UUID → metadata

        # -----------------------------
        # 2. Build reference variables
        # -----------------------------
        for color, label, value, fig_id in matches:
            uuid_prefix = value.split("-")[0] if "-" in value else value[:8]
            variable_name = f"{label}_{uuid_prefix}"
            display_name = f"@{variable_name}"

            if variable_name in reference_map.values():
                raise ValueError(f"Duplicate variable name: {variable_name}")

            reference_map[value] = variable_name
            reference_objects[value] = {
                "label": label,
                "color": color,
                "fig_id": fig_id,
                "variable_name": variable_name,
                "display_name": display_name,
            }

        # -----------------------------
        # 3. Replace references in text
        # -----------------------------
        contextualized_text = message.text
        for color, label, value, fig_id in matches:
            original = f"#{color}[{label}]({value}@{fig_id})"
            display_name = reference_objects[value]["display_name"]
            contextualized_text = contextualized_text.replace(original, display_name)

        # -----------------------------
        # 4. Process attachments & objects
        # -----------------------------
        paths = []

        for attachment in message.attachments:
            if not isinstance(attachment, Image):
                raise ValueError("Attachments must be Image")

            # Frame references: label == image
            for uuid_value, ref_data in reference_objects.items():
                if (
                    ref_data["label"] == "image"
                    and ref_data["fig_id"] == attachment.id
                ):
                    variable_name = ref_data["variable_name"]

                    if variable_name in context:
                        raise ValueError(f"Reference {variable_name} already exists")

                    context[variable_name] = Attachment(attachment)
                    paths.append(variable_name)
                    reference_objects[uuid_value]["processed"] = True

            # Object references: point, box, text, scribble
            for obj in attachment.objects:
                normalized_obj = self._normalize_attachment_object(obj)
                if normalized_obj is None:
                    continue

                obj_id = getattr(normalized_obj, "id", None)
                if obj_id and obj_id in reference_map:
                    variable_name = reference_map[obj_id]

                    if variable_name in context:
                        raise ValueError(f"Reference {variable_name} already exists")

                    context[variable_name] = Attachment(normalized_obj)
                    paths.append(variable_name)
                    reference_objects[obj_id]["processed"] = True

                    if getattr(normalized_obj, "is_ephemeral", False):
                        attachment.remove_object(obj)

            # If this attachment was *not* referenced, create image_i
            attachment_was_referenced = any(
                ref.get("processed") and ref["label"] == "image"
                for ref in reference_objects.values()
            )

            if not attachment_was_referenced:
                variable_name = self._get_image_variable_name(context)
                context[variable_name] = Attachment(attachment)
                paths.append(variable_name)

        # -----------------------------
        # 5. Verify all references were matched
        # -----------------------------
        unprocessed_refs = [
            ref_data["variable_name"]
            for ref_data in reference_objects.values()
            if not ref_data.get("processed")
        ]

        if unprocessed_refs:
            display_names = [
                ref_data["display_name"]
                for ref_data in reference_objects.values()
                if ref_data["variable_name"] in unprocessed_refs
            ]
            raise ValueError(f"Unmatched references: {', '.join(display_names)}")

        print(contextualized_text)
        print(message.text)

        return ContextualizedMessage(
            text=contextualized_text,
            paths=paths
        )

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

    def _normalize_attachment_object(
        self, obj: Any
    ) -> Union[Image, Object, Point, Box, Text, None]:
        """Convert raw Fabric objects into their referent-aware counterparts."""
        if isinstance(obj, (Image, Object, Point, Box, Text)):
            return obj

        if isinstance(obj, FabricRect):
            return Box.model_validate(obj.model_dump())

        if isinstance(obj, FabricText):
            return Text.model_validate(obj.model_dump())

        return None
