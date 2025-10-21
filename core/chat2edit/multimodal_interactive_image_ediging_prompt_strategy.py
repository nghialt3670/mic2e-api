from chat2edit.models import Feedback
from chat2edit.prompting.strategies import OtcStrategy
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
            params_with_lengths = [f"{param} (length: {length})" for param, length in zip(feedback.parameters, feedback.lengths)]
            params_str = ", ".join(params_with_lengths)
            return f"In function `{feedback.function}`, parameter lengths do not match: {params_str}."
        
        elif isinstance(feedback, MissingAllOptionalParametersFeedback):
            params_str = ", ".join(feedback.parameters)
            return f"In function `{feedback.function}`, all optional parameters are missing: {params_str}."
        
        # Fall back to parent implementation for other feedbacks
        return super().create_feedback_text(feedback)
