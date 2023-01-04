from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from ...core.constants.employee_roles import EmployeeRole
from ...core.constants.regex import phone_number, pin_code


class UserType(Enum):
    EMPLOYEE = "employee"
    CUSTOMER = "customer"


class CreateEmployeeSchema(BaseModel):
    first_name: str
    last_name: str | None = None
    phone_number: str = Field(regex=phone_number, example="+254787654321")
    password: str = Field(regex=pin_code, example="12345")
    roles: list[EmployeeRole] = []
    info: dict = {}
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        use_enum_values = True


class UserBaseSchema(BaseModel):
    first_name: str
    last_name: str | None = None
    user_type: UserType
    photo: str | None = None
    roles: list[str] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        use_enum_values = True


class LoginUserSchema(BaseModel):
    phone_number: str = Field(regex=phone_number, example="+254787654321")
    password: str = Field(regex=pin_code, example="12345")


class UserResponseSchema(UserBaseSchema):
    id: str = Field(..., alias='_id')


class CreateUserResponseSchema(BaseModel):
    success: bool
    user: UserResponseSchema | None


class LoginUserResponseSchema(BaseModel):
    success: bool
    user: UserResponseSchema | None
    access_token: str
    refresh_token: str


class RefreshTokenResponseSchema(BaseModel):
    success: bool
    access_token: str


class ChangePasswordResponseSchema(BaseModel):
    success: bool


class LogoutResponseSchema(BaseModel):
    success: bool
