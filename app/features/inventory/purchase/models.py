from datetime import datetime
from pydantic import BaseModel, Field
from app.core.constants.measurement_units import MeasurementUnit


class PurchaseBaseModel(BaseModel):
    item: str
    amount: float = Field(gt=0)
    unit: MeasurementUnit
    purchased_at: datetime = datetime.utcnow()
    price: float

    class Config:
        use_enum_values = True


class PurchaseReadModel(PurchaseBaseModel):
    id: str = Field(..., alias="_id")
    purchased_by: str
    updated_at: datetime | None = None
    updated_by: str | None = None


class PurchaseUpdateModel(BaseModel):
    item: str | None = None
    amount: float | None = Field(gt=0, default=None)
    unit: MeasurementUnit | None = None
    price: float | None = None
    purchased_by: str | None = None
    purchased_at: datetime | None = None


class SinglePurchaseResponseModel(BaseModel):
    success: bool
    purchase: PurchaseReadModel


class MultiplePurchasesResponseModel(BaseModel):
    success: bool
    purchases: list[PurchaseReadModel]
