from typing import Any
from pydantic import BaseModel


class ErrorModel(BaseModel):
    type: str = "type"
    message: str = "message"
    location: Any = "location"
    
class ErrorResponseModel(BaseModel):
    success: bool = False
    errors: list[ErrorModel]
    