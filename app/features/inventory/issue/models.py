from datetime import datetime
from pydantic import BaseModel, Field
from app.core.constants.measurement_units import MeasurementUnit


class IssueBaseModel(BaseModel):
    item: str
    amount: float = Field(gt=0)
    unit: MeasurementUnit
    issued_at: datetime = datetime.utcnow()

    class Config:
        use_enum_values = True


class IssueReadModel(IssueBaseModel):
    id: str = Field(..., alias="_id")
    cost: float
    issued_by: str
    updated_at: datetime | None = None
    updated_by: str | None = None


class IssueUpdateModel(BaseModel):
    item: str | None = None
    amount: float | None = Field(gt=0, default=None)
    unit: MeasurementUnit | None = None
    cost: float | None = None
    issued_by: str | None = None
    issued_at: datetime | None = None


class SingleIssueResponseModel(BaseModel):
    success: bool
    issue: IssueReadModel


class MultipleIssuesResponseModel(BaseModel):
    success: bool
    issues: list[IssueReadModel]
