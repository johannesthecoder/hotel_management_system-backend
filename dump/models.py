from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from ...core.constants.employee_roles import EmployeeRole
from ...core.constants.regex import phone_number


class EmployeeBaseSchema(BaseModel):
    first_name: str
    last_name: str | None = None
    phone_number: str = Field(regex=phone_number, example="+254787654321")
    roles: list[EmployeeRole] = []
    info: dict = {}
    is_active: bool = True
    created_at: datetime | None = None
    created_by: datetime | None = None
    updated_at: datetime | None = None
    updated_by: datetime | None = None
    id: str = Field(..., alias="_id")

    class Config:
        use_enum_values = True


class EmployeeUpdateModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = Field(
        regex=phone_number, example="+254787654321", default=None)
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SingleEmployeeResponseSchema(BaseModel):
    success: bool
    employee: EmployeeBaseSchema


class MultipleEmployeeResponseModel(BaseModel):
    success: bool
    employees: list[EmployeeBaseSchema]
