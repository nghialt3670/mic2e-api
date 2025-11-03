from pydantic import Field

from chat2edit.models import ContextualizedFeedback

class LabelBasedObjectExtractionQuantityMismatchFeedback(ContextualizedFeedback):
    label: str = Field(description="The label of the objects")
    num_expected_objects: int = Field(description="The number of expected objects")
    num_extracted_objects: int = Field(description="The number of extracted objects")
