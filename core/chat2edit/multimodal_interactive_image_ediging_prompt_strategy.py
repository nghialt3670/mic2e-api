from chat2edit.models import Feedback
from chat2edit.prompting.strategies import OtcStrategy
from typing_extensions import override


class MultimodalInteractiveImageEditingPromptStrategy(OtcStrategy):
    @override
    def create_feedback_text(self, feedback: Feedback) -> str:
        return super().create_feedback_text(feedback)
