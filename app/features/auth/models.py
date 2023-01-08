from pydantic import BaseModel
from ..account.employee.models import EmployeeReadModel
from ..account.customer.models import CustomerReadModel


class EmployeeLoginResponseModel(BaseModel):
    success: bool
    employee: EmployeeReadModel
    access_token: str
    refresh_token: str


class CustomerLoginResponseModel(BaseModel):
    success: bool
    customer: CustomerReadModel
    access_token: str
    refresh_token: str


class RefreshTokenResponseModel(BaseModel):
    success: bool
    access_token: str


class LogoutResponseModel(BaseModel):
    success: bool
