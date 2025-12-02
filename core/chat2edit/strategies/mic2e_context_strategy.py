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

from core.chat2edit.models import Box, Image, Object, Point, Scribble, Text
from core.chat2edit.models.fabric.objects import FabricRect, FabricText

CONTEXT_VALUE_BASE_TYPE = Union[
    Image,
    Object,
    Box,
    Point,
    Text,
    Scribble,
    int,
    str,
    float,
    bool,
]
# Single allowed item type (value or list of values) used for filtering
CONTEXT_ITEM_TYPE = Union[CONTEXT_VALUE_BASE_TYPE, List[CONTEXT_VALUE_BASE_TYPE]]
CONTEXT_TYPE = Dict[str, Union[CONTEXT_VALUE_BASE_TYPE, List[CONTEXT_VALUE_BASE_TYPE]]]


class Mic2eContextStrategy(ContextStrategy):
    def __init__(self) -> None:
        super().__init__()

    def filter_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        filtered_context: Dict[str, Any] = {}
        # We validate individual values (or lists), not the whole dict
        item_adapter = TypeAdapter(CONTEXT_ITEM_TYPE)

        for key, value in context.items():
            # If this is an Attachment, unwrap to its underlying Pydantic model
            from chat2edit.context.attachments import Attachment

            base_value = value.__obj__ if isinstance(value, Attachment) else value

            try:
                item_adapter.validate_python(base_value)
                filtered_context[key] = base_value
            except Exception:
                # Drop non-serializable / unsupported values (functions, etc.)
                continue

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

            # If this attachment was *not* referenced, create image_<idprefix>
            attachment_was_referenced = any(
                ref.get("processed") and ref["label"] == "image"
                for ref in reference_objects.values()
            )

            if not attachment_was_referenced:
                variable_name = self._get_image_variable_name(
                    context, getattr(attachment, "id", None)
                )
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

    def _get_image_variable_name(
        self, context: Dict[str, Any], attachment_id: str | None
    ) -> str:
        """
        Generate a stable image variable name based on the attachment id.

        If an attachment id is provided, use the first segment of the UUID as a
        suffix (e.g. image_5a00b15a). If that name is already taken or no id is
        available, fall back to an incrementing index.
        """
        existing_variable_names = set(context.keys())

        if attachment_id:
            uuid_prefix = (
                attachment_id.split("-")[0] if "-" in attachment_id else attachment_id[:8]
            )
            candidate = f"image_{uuid_prefix}"
            if candidate not in existing_variable_names:
                return candidate

        # Fallback: image_1, image_2, ...
        for i in range(1, 100):
            variable_name = f"image_{i}"
            if variable_name not in existing_variable_names:
                return variable_name

        raise RuntimeError("Too many images in context")

    def _normalize_attachment_object(
        self, obj: Any
    ) -> Union[Image, Object, Point, Box, Text, Scribble, None]:
        """Convert raw Fabric objects into their referent-aware counterparts."""
        if isinstance(obj, (Image, Object, Point, Box, Text, Scribble)):
            return obj

        # Get is_ephemeral from the original object if it exists
        is_ephemeral = getattr(obj, "is_ephemeral", False)

        if isinstance(obj, FabricRect):
            box_data = obj.model_dump()
            box_data["is_ephemeral"] = is_ephemeral
            return Box.model_validate(box_data)

        if isinstance(obj, FabricText):
            text_data = obj.model_dump()
            text_data["is_ephemeral"] = is_ephemeral
            return Text.model_validate(text_data)

        # Handle FabricCircle (Point) and FabricPath (Scribble)
        from core.chat2edit.models.fabric.objects import FabricCircle, FabricPath

        if isinstance(obj, FabricCircle):
            circle_data = obj.model_dump()
            circle_data["is_ephemeral"] = is_ephemeral
            return Point.model_validate(circle_data)

        if isinstance(obj, FabricPath):
            path_data = obj.model_dump()
            path_data["is_ephemeral"] = is_ephemeral
            return Scribble.model_validate(path_data)

        return None
