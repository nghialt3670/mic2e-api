from typing import List

from chat2edit.models import Feedback
from pydantic import Field


class MismatchListParametersFeedback(Feedback):
    function: str = Field(description="Name of the function that raised the feedback")
    parameters: List[str] = Field(description="Names of the parameters")
    lengths: List[int] = Field(description="Lengths of the parameters")
