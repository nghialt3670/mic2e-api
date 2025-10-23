from typing import List

from pydantic import BaseModel


class MessageModel(BaseModel):
    text: str
    attachment_urls: List[str]
