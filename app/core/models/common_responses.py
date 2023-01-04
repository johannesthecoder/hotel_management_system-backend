from pydantic import BaseModel


class UpdateResponseModel(BaseModel):
    success: bool
