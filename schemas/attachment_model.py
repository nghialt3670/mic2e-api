from pydantic import BaseModel

class AttachmentModel(BaseModel):
    context_path: str
    original_filename: str
    path: str
    url: str