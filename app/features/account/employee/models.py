from datetime import datetime
from pydantic import BaseModel, Field
from ....core.constants.regex import phone_number
from ....core.constants.employee_roles import EmployeeRole


class EmployeeBaseModel(BaseModel):
    first_name: str
    last_name: str | None = None
    phone_number: str = Field(regex=phone_number, example="+254787654321")
    roles: list[EmployeeRole] = []
    is_active: bool = True

    class Config:
        use_enum_values = True


class EmployeeReadModel(EmployeeBaseModel):
    id: str = Field(..., alias="_id")
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None


class EmployeeUpdateModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = Field(
        default=None, regex=phone_number, example="+254787654321"
    )


class SingleEmployeeResponseModel(BaseModel):
    success: bool
    employee: EmployeeReadModel


class MultipleEmployeeResponseModel(BaseModel):
    success: bool
    employees: list[EmployeeReadModel]
