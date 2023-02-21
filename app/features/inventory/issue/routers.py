from datetime import datetime
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, Query
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


inventory_issue_router = APIRouter()

inventory_issue_router.tags = ["Inventory - Issues"]


@inventory_issue_router.post(
    "/", response_model=models.SingleIssueResponseModel
)
async def issue_item(
    new_issue: models.IssueBaseModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.ISSUE)
    ),
):
    if not ObjectId.is_valid(new_issue.item):
        raise_unprocessable_value_exception(
            message="invalid item id",
            location=["request body", "item"],
        )

    item = await item_controller.find_item_by_id(id=new_issue.item)

    if not item:
        raise_not_found_exception(
            message=f"not item found with id={new_issue.item}",
            location=["request body", "item"],
        )

    if not is_same_measurement_type(item["unit"], new_issue.unit):
        raise_unprocessable_value_exception(
            message="the item is not measured with the same type of measurement.",
            location=["request body", "unit"],
        )

    issue_cost = (
        item["cost"]
        * new_issue.amount
        * (
            measurement_unit_value[new_issue.unit]
            / measurement_unit_value[item["unit"]]
        )
    )

    issue_id = await controller.issue_item(
        new_issue={**new_issue.dict(), "cost": issue_cost},
        issued_by=current_user_id,
    )

    issue = await controller.find_issue_by_id(id=issue_id)

    if not issue:
        raise_operation_failed_exception(message="problem while issuing item")

    return models.SingleIssueResponseModel(
        success=True,
        issue=dict_to_model(model=models.IssueReadModel, dict_model=issue),
    )


@inventory_issue_router.get(
    "/{issue_id}", response_model=models.SingleIssueResponseModel
)
async def get_issue_by_id(
    issue_id: str,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_ISSUE)
    ),
):
    if not ObjectId.is_valid(issue_id):
        raise_unprocessable_value_exception(
            message="invalid issue id",
            location=["path parameter", "issue_id"],
        )

    issue = await controller.find_issue_by_id(id=issue_id)

    if not issue:
        raise_not_found_exception(
            message=f"no issue found with an id={issue_id}",
            location=["path parameter", "issue_id"],
        )

    return models.SingleIssueResponseModel(
        success=True,
        issue=dict_to_model(
            model=models.IssueReadModel,
            dict_model=issue,
        ),
    )


@inventory_issue_router.get(
    "/", response_model=models.MultipleIssuesResponseModel
)
async def get_issues(
    item: str | None = None,
    issued_by: str | None = None,
    issued_at_from: datetime | None = None,
    issued_at_to: datetime | None = None,
    limit: int = 0,
    skip: int = 0,
    sort_by: list[str] = Query(
        description="append +[for ascending] or -[for descending] before the name to be sorted with. NOTE: (1) no space between the sign and the name, (2) the arrangement/order of the array maters ..."
    ),
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_ISSUE)
    ),
):
    if item and not ObjectId.is_valid(item):
        raise_unprocessable_value_exception(
            message="invalid item id",
            location=["query parameter", "item"],
        )

    if issued_by and not ObjectId.is_valid(issued_by):
        raise_unprocessable_value_exception(
            message="invalid item id",
            location=["query parameter", "issued_by"],
        )

    issues = await controller.find_many_issues(
        item=item,
        issued_by=issued_by,
        issued_at_from=issued_at_from,
        issued_at_to=issued_at_to,
        limit=limit,
        skip=skip,
        sort_by=sort_by,
    )

    if not type(issues) == list:
        raise_operation_failed_exception(
            message="problem while getting issue"
        )

    return models.MultipleIssuesResponseModel(
        success=True,
        issues=[
            dict_to_model(
                model=models.IssueReadModel,
                dict_model=issue,
            )
            for issue in issues
        ],
    )


@inventory_issue_router.patch(
    "/{issue_id}", response_model=models.SingleIssueResponseModel
)
async def update_issue(
    issue_id: str,
    updated_issue: models.IssueUpdateModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.UPDATE_ISSUE)
    ),
):
    if not ObjectId.is_valid(issue_id):
        raise_unprocessable_value_exception(
            message="invalid issue id",
            location=["path parameter", "issue_id"],
        )

    if updated_issue.issued_by and not ObjectId.is_valid(
        updated_issue.issued_by
    ):
        raise_unprocessable_value_exception(
            message="invalid item id",
            location=["request body", "issued_by"],
        )

    if updated_issue.item and not ObjectId.is_valid(updated_issue.item):
        raise_unprocessable_value_exception(
            message="invalid item id",
            location=["request body", "item"],
        )

    if updated_issue.item:
        item = await item_controller.find_item_by_id(id=updated_issue.item)

        if not item:
            raise_not_found_exception(
                message=f"no item found with an id={updated_issue.item}",
                location=["request body", "item"],
            )

    if not updated_issue.cost and (
        updated_issue.amount or updated_issue.unit or updated_issue.item
    ):
        if not updated_issue.item:
            issue = dict(await controller.find_issue_by_id(id=issue_id))
            item = await item_controller.find_item_by_id(
                id=str(issue.get("item"))
            )
        if type(updated_issue.amount) == None:
            issue = dict(await controller.find_issue_by_id(id=issue_id))
            updated_issue.amount = issue.get("amount")

        if not updated_issue.unit:
            issue = dict(await controller.find_issue_by_id(id=issue_id))
            updated_issue.amount = issue.get("unit")

        updated_issue.cost = (
            item["cost"]
            * updated_issue.amount
            * (
                measurement_unit_value[updated_issue.unit]
                / measurement_unit_value[item["unit"]]
            )
        )

    if await controller.update_issue(
        id=issue_id,
        updated_issue=model_to_dict_without_None(model=updated_issue),
        updated_by=current_user_id,
    ):
        issue = await controller.find_issue_by_id(id=issue_id)

        if issue:
            return models.SingleIssueResponseModel(
                success=True,
                issue=dict_to_model(
                    model=models.IssueReadModel, dict_model=issue
                ),
            )
    raise_operation_failed_exception(message="problem while updating issue")
