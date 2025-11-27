from typing import Optional

from pydantic import BaseModel, Field


class Referent(BaseModel):
    is_ephemeral: bool = Field(
        default=False, description="Whether the referent is ephemeral"
    )
