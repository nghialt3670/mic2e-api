from chat2edit.models import Feedback
from pydantic import Field


class LabelBasedObjectExtractionQuantityMismatchFeedback(Feedback):
    label: str = Field(description="The label of the objects")
    num_expected_objects: int = Field(description="The number of expected objects")
    num_extracted_objects: int = Field(description="The number of extracted objects")
