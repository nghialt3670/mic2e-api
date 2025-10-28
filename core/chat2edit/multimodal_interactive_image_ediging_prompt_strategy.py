import inspect
from typing import Any, Dict

from chat2edit.models import Feedback
from chat2edit.prompting.strategies import OtcStrategy
from chat2edit.prompting.stubbing.stubs import CodeStub, FunctionStub, ClassStub
from typing_extensions import override

from core.chat2edit.feedbacks import (
    EmptyListParametersFeedback,
    MismatchListParametersFeedback,
    MissingAllOptionalParametersFeedback,
    ObjectExtractionQuantityMismatchFeedback,
)


class MultimodalInteractiveImageEditingPromptStrategy(OtcStrategy):
    @override
    def create_feedback_text(self, feedback: Feedback) -> str:
        # Handle custom feedbacks first
        if isinstance(feedback, ObjectExtractionQuantityMismatchFeedback):
            return f"Expected to extract {feedback.num_expected_objects} object(s), but found {feedback.num_extracted_objects} object(s)."

        elif isinstance(feedback, EmptyListParametersFeedback):
            params_str = ", ".join(feedback.parameters)
            return f"In function `{feedback.function}`, the following parameters are empty: {params_str}."

        elif isinstance(feedback, MismatchListParametersFeedback):
            params_with_lengths = [
                f"{param} (length: {length})"
                for param, length in zip(feedback.parameters, feedback.lengths)
            ]
            params_str = ", ".join(params_with_lengths)
            return f"In function `{feedback.function}`, parameter lengths do not match: {params_str}."

        elif isinstance(feedback, MissingAllOptionalParametersFeedback):
            params_str = ", ".join(feedback.parameters)
            return f"In function `{feedback.function}`, all optional parameters are missing: {params_str}."

        # Fall back to parent implementation for other feedbacks
        return super().create_feedback_text(feedback)

    @override
    def create_context_code(self, context: Dict[str, Any]) -> str:
        """
        Override to force creation of function stubs instead of imports.
        
        The default implementation uses is_external_package() which checks if the module
        starts with "chat2edit". Since our functions are in "core.chat2edit.*", they're
        detected as external and converted to imports. This override forces them to be
        rendered as function stubs.
        """
        blocks = []
        
        for k, v in context.items():
            if not inspect.isclass(v) and not inspect.isfunction(v):
                continue
            
            # Always create stubs for classes and functions, never imports
            if inspect.isclass(v):
                blocks.append(ClassStub.from_class(v))
            elif inspect.isfunction(v):
                blocks.append(FunctionStub.from_function(v))
        
        # Create a CodeStub with our blocks
        code_stub = CodeStub(blocks=blocks)
        return code_stub.generate()
