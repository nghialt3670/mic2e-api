from typing import Optional

from pydantic import BaseModel, Field


class Referent(BaseModel):
    reference: Optional[str] = Field(
        default=None, description="Reference name to the referent"
    )
    is_ephemeral: bool = Field(
        default=False, description="Whether the referent is ephemeral"
    )
