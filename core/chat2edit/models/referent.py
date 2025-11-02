from pydantic import BaseModel, Field


class Referent(BaseModel):
    reference: str = Field(description="Reference name to the referent")
    is_ephemeral: bool = Field(
        default=False, description="Whether the referent is ephemeral"
    )
