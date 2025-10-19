from chat2edit.models import Feedback
from pydantic import Field


class ObjectExtractionQuantityMismatchFeedback(Feedback):
    num_expected_objects: int = Field(description="The number of expected objects")
    num_extracted_objects: int = Field(description="The number of extracted objects")
