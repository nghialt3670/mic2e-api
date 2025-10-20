from typing import List, Union

from chat2edit.execution.decorators import feedback_invalid_parameter_type, respond
from chat2edit.models import Message

from core.chat2edit.models.image import Image
from core.chat2edit.models.object import Object


@respond
@feedback_invalid_parameter_type
def respond_to_user(text: str, attachments: List[Union[Image, Object]] = []) -> str:
    return Message(text=text, attachments=attachments)
