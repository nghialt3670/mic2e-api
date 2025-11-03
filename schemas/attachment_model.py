from pydantic import BaseModel, Field


class AttachmentModel(BaseModel):
    filename: str = Field(description="The filename of the attachment")
    upload_path: str = Field(description="The path of the attachment in the storage")
    upload_url: str = Field(description="The url of the attachment in the storage")
