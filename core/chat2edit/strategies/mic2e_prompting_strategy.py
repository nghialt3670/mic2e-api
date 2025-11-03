from chat2edit.models import ContextualizedFeedback
from chat2edit.prompting.strategies import OtcPromptingStrategy

from core.chat2edit.feedbacks import LabelBasedObjectExtractionQuantityMismatchFeedback

LABEL_BASED_OBJECT_EXTRACTION_QUANTITY_MISMATCH_FEEDBACK_TEXT = "Expected to extract {num_expected_objects} object(s) with label '{label}', but found {num_extracted_objects} object(s)."


class Mic2ePromptingStrategy(OtcPromptingStrategy):
    def __init__(self) -> None:
        super().__init__()

    def create_feedback_text(self, feedback: ContextualizedFeedback) -> str:
        if isinstance(feedback, LabelBasedObjectExtractionQuantityMismatchFeedback):
            return LABEL_BASED_OBJECT_EXTRACTION_QUANTITY_MISMATCH_FEEDBACK_TEXT.format(
                label=feedback.label,
                num_expected_objects=feedback.num_expected_objects,
                num_extracted_objects=feedback.num_extracted_objects,
            )

        return super().create_feedback_text(feedback)
