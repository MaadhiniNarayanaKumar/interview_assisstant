from typing import Any

from pydantic import (
    BaseModel,
    ValidationError,
    ValidationInfo,
    field_validator, model_validator, Field
)


class Interaction(BaseModel):
    query: str | None = Field(
        default=None, title="Interaction Query to SmartPak AI Model", max_length=1000
    )