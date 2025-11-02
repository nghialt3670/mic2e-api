from typing import Generic, Optional, TypeVar

from pydantic import Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class ResponseModel(GenericModel, Generic[T]):
    code: int = Field(default=200, description="The code of the response")
    message: Optional[str] = Field(
        default=None, description="The message of the response"
    )
    data: T = Field(description="The data of the response")
