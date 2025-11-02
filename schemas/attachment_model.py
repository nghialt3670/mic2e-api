from pydantic import BaseModel


class AttachmentModel(BaseModel):
    context_path: str
    original_filename: str
    upload_path: str
    upload_url: str
