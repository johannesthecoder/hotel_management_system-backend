from datetime import datetime
from pydantic import BaseModel, Field
from app.core.constants.measurement_units import MeasurementUnit


class CategoryBaseModel(BaseModel):
    name: str


class CategoryReadModel(CategoryBaseModel):
    id: str = Field(..., alias="_id")
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None


class CategoryUpdateModel(BaseModel):
    name: str | None = None


class SingleCategoryResponseModel(BaseModel):
    success: bool
    category: CategoryReadModel


class MultipleCategoriesResponseModel(BaseModel):
    success: bool
    categories: list[CategoryReadModel] = []


class GroupBaseModel(BaseModel):
    name: str
    category: str


class GroupReadModel(GroupBaseModel):
    id: str = Field(..., alias="_id")
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None


class GroupUpdateModel(BaseModel):
    name: str | None = None
    category: str | None = None


class SingleGroupResponseModel(BaseModel):
    success: bool
    group: GroupReadModel


class MultipleGroupsResponseModel(BaseModel):
    success: bool
    groups: list[GroupReadModel] = []


class ItemBaseModel(BaseModel):
    name: str
    group: str
    unit: MeasurementUnit
    quantity: float
    minimum_quantity: float
    average_life_expectancy: float
    cost: float


class ItemReadModel(ItemBaseModel):
    id: str = Field(..., alias="_id")
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None


class ItemUpdateModel(BaseModel):
    name: str | None = None
    group: str | None = None
    unit: MeasurementUnit | None = None
    minimum_quantity: float | None = None
    average_life_expectancy: float | None = None
    cost: float | None = None


class SingleItemResponseModel(BaseModel):
    success: bool
    item: ItemReadModel


class MultipleItemsResponseModel(BaseModel):
    success: bool
    items: list[ItemReadModel] = []
