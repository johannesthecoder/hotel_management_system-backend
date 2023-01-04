from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from ....core.constants.regex import phone_number


class CustomerBaseModel(BaseModel):
    first_name: str
    last_name: str | None = None
    nationality: str
    passport_number: str
    email: EmailStr | None = None
    phone_number: str = Field(regex=phone_number, example="+254787654321")
    is_active: bool = True


class CustomerReadModel(CustomerBaseModel):
    id: str = Field(..., alias="_id")
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None


class CustomerUpdateModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    nationality: str | None = None
    passport_number: str | None = None
    phone_number: str | None = Field(
        default=None, regex=phone_number, example="+254787654321"
    )


class SingleCustomerResponseModel(BaseModel):
    success: bool
    customer: CustomerReadModel


class MultipleCustomerResponseModel(BaseModel):
    success: bool
    customers: list[CustomerReadModel]
