from datetime import datetime
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends
from ....core.constants.measurement_units import (
    is_same_measurement_type,
    measurement_unit_value,
)
from ....core.error.exceptions import (
    raise_not_found_exception,
    raise_operation_failed_exception,
    raise_unprocessable_value_exception,
)
from ....core.utilities.converter import (
    dict_to_model,
    model_to_dict_without_None,
)
from ....core.utilities.jwt_config import AuthJWT, EmployeeRoleChecker
from ....core.constants.employee_roles import EmployeeRole
from ..item import controller as item_controller
from . import models
from . import controller


inventory_purchase_router = APIRouter()

inventory_purchase_router.tags = ["Inventory - Purchase"]


@inventory_purchase_router.post(
    "/", response_model=models.SinglePurchaseResponseModel
)
async def purchase_item(
    new_purchase: models.PurchaseBaseModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.PURCHASE)
    ),
):
    if not ObjectId.is_valid(new_purchase.item):
        raise_unprocessable_value_exception(
            message="invalid item id",
            location=["request body", "item"],
        )

    item = await item_controller.find_item_by_id(id=new_purchase.item)

    if not item:
        raise_not_found_exception(
            message=f"not item found with id={new_purchase.item}",
            location=["request body", "item"],
        )

    if not is_same_measurement_type(item["unit"], new_purchase.unit):
        raise_unprocessable_value_exception(
            message="the item is not measured with the same type of measurement.",
            location=["request body", "unit"],
        )

    purchase_id = await controller.purchase_item(
        new_purchase=new_purchase.dict(),
        purchased_by=current_user_id,
    )

    purchase = await controller.find_purchase_by_id(id=purchase_id)

    if not purchase:
        raise_operation_failed_exception(message="problem while issuing item")

    return models.SinglePurchaseResponseModel(
        success=True,
        purchase=dict_to_model(
            model=models.PurchaseReadModel, dict_model=purchase
        ),
    )


@inventory_purchase_router.get(
    "/{purchase_id}", response_model=models.SinglePurchaseResponseModel
)
async def get_purchase_by_id(
    purchase_id: str,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_PURCHASE)
    ),
):
    if not ObjectId.is_valid(purchase_id):
        raise_unprocessable_value_exception(
            message="invalid purchase id",
            location=["path parameter", "purchase_id"],
        )

    purchase = await controller.find_purchase_by_id(id=purchase_id)

    if not purchase:
        raise_not_found_exception(
            message=f"no purchase found with an id={purchase_id}",
            location=["path parameter", "purchase_id"],
        )

    return models.SinglePurchaseResponseModel(
        success=True,
        purchase=dict_to_model(
            model=models.PurchaseReadModel,
            dict_model=purchase,
        ),
    )


@inventory_purchase_router.get(
    "/", response_model=models.MultiplePurchasesResponseModel
)
async def get_purchases(
    item: str | None = None,
    purchased_by: str | None = None,
    purchased_at_from: datetime | None = None,
    purchased_at_to: datetime | None = None,
    limit: int | None = None,
    skip: int = 0,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_PURCHASE)
    ),
):
    if item and not ObjectId.is_valid(item):
        raise_unprocessable_value_exception(
            message="invalid item id",
            location=["query parameter", "item"],
        )

    if purchased_by and not ObjectId.is_valid(purchased_by):
        raise_unprocessable_value_exception(
            message="invalid item id",
            location=["query parameter", "purchased_by"],
        )

    purchases = await controller.find_many_purchases(
        item=item,
        purchased_by=purchased_by,
        purchased_at_from=purchased_at_from,
        purchased_at_to=purchased_at_to,
        limit=limit,
        skip=skip,
    )

    if not type(purchases) == list:
        raise_operation_failed_exception(
            message="problem while getting purchase"
        )

    return models.MultiplePurchasesResponseModel(
        success=True,
        purchases=[
            dict_to_model(
                model=models.PurchaseReadModel,
                dict_model=purchase,
            )
            for purchase in purchases
        ],
    )


@inventory_purchase_router.patch(
    "/{purchase_id}", response_model=models.SinglePurchaseResponseModel
)
async def update_purchase(
    purchase_id: str,
    updated_purchase: models.PurchaseUpdateModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.UPDATE_PURCHASE)
    ),
):
    if not ObjectId.is_valid(purchase_id):
        raise_unprocessable_value_exception(
            message="invalid purchase id",
            location=["path parameter", "purchase_id"],
        )

    if updated_purchase.purchased_by and not ObjectId.is_valid(
        updated_purchase.purchased_by
    ):
        raise_unprocessable_value_exception(
            message="invalid item id",
            location=["request body", "purchased_by"],
        )

    if updated_purchase.item and not ObjectId.is_valid(updated_purchase.item):
        raise_unprocessable_value_exception(
            message="invalid item id",
            location=["request body", "item"],
        )

    item = {}

    if updated_purchase.item:
        item = dict(
            await item_controller.find_item_by_id(id=updated_purchase.item)
        )

        if not item:
            raise_not_found_exception(
                message=f"no item found with an id={updated_purchase.item}",
                location=["request body", "item"],
            )
    else:
        old_purchase = dict(
            await controller.find_purchase_by_id(id=purchase_id)
        )
        item = dict(
            await item_controller.find_item_by_id(id=old_purchase.get("item"))
        )

    if updated_purchase.unit:
        if not is_same_measurement_type(item["unit"], updated_purchase.unit):
            raise_unprocessable_value_exception(
                message="the item is not measured with the same type of measurement.",
                location=["request body", "unit"],
            )
    else:
        if not is_same_measurement_type(item["unit"], old_purchase["unit"]):
            raise_unprocessable_value_exception(
                message="the item is not measured with the same type of measurement.",
                location=["request body", "unit"],
            )

    if await controller.update_purchase(
        id=purchase_id,
        updated_purchase=model_to_dict_without_None(model=updated_purchase),
        updated_by=current_user_id,
    ):
        purchase = await controller.find_purchase_by_id(id=purchase_id)

        if purchase:
            return models.SinglePurchaseResponseModel(
                success=True,
                purchase=dict_to_model(
                    model=models.PurchaseReadModel, dict_model=purchase
                ),
            )
    raise_operation_failed_exception(
        message="problem while updating purchase"
    )
