from typing import Any
from pydantic import BaseModel


class ErrorSchema(BaseModel):
    type: str = "type"
    message: str = "message"
    location: Any = "location"


class ErrorResponseSchema(BaseModel):
    success: bool = False
    errors: list[ErrorSchema]
