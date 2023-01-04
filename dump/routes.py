from re import match
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, Query
from ...core.constants.employee_roles import EmployeeRole
from ...core.models.common_responses import UpdateResponseSchema
from ...core.constants.regex import pin_code
from ...core.utilities.jwt_config import (
    AuthJWT,
    EmployeeRoleChecker,
    require_user,
)
from ...core.utilities.password import hash_password, verify_password
from ...core.utilities.converter import dict_to_model
from ...core.error.exceptions import (
    raise_not_found_exception,
    raise_operation_failed_exception,
    raise_unauthorized_exception,
    raise_unknown_error_exception,
    raise_unprocessable_value_exception,
)
from .models import (
    EmployeeBaseSchema,
    MultipleEmployeeResponseModel,
    SingleEmployeeResponseSchema,
)
from . import controller

account_router = APIRouter()
account_router.tags = ["Account"]


@account_router.get("/mine", response_model=SingleEmployeeResponseSchema)
async def get_my_account(user_id: AuthJWT = Depends(require_user)):
    account = await controller.find_employee_by_id(id=user_id)

    if not account:
        raise_unknown_error_exception(
            message="problem while getting user/account details"
        )

    return SingleEmployeeResponseSchema(
        success=True,
        employee=dict_to_model(model=EmployeeBaseSchema, dict_model=account),
    )


@account_router.patch(
    "/change_my_password", response_model=UpdateResponseSchema
)
async def change_my_password(
    old_password: str,
    new_password: str,
    user_id: AuthJWT = Depends(require_user),
):
    if not match(pin_code, new_password):
        raise_unprocessable_value_exception(
            message="invalid/incorrect new password. should contain minimum of 5 and maximum of 15 digits",
            location=["request body", "new_password"],
        )

    employee = await controller.find_employee_by_id(id=user_id)

    if not verify_password(
        password=old_password, hashed_password=employee["password"]
    ):
        raise_unauthorized_exception(
            message="old password is incorrect",
            location=["request body", "old_password"],
        )

    new_password = hash_password(password=new_password)

    if not await controller.update_employee_password(
        id=user_id, new_password=new_password, updated_by=user_id
    ):
        raise_operation_failed_exception(
            message="could not change password", location=["unknown"]
        )

    return UpdateResponseSchema(success=True)


@account_router.get("/", response_model=MultipleEmployeeResponseModel)
async def get_accounts(
    name: str | None = None,
    phone_number: str | None = None,
    roles: list[EmployeeRole] = Query(default=[]),
    is_active: bool | None = None,
    _: AuthJWT = Depends(EmployeeRoleChecker(EmployeeRole.VIEW_EMPLOYEES)),
):
    employees = await controller.find_employees_by_filter(
        name=name,
        phone_number=phone_number,
        roles=[role.value for role in roles],
        is_active=is_active,
    )

    return MultipleEmployeeResponseModel(
        success=False,
        employees=[
            dict_to_model(dict_model=employee, model=EmployeeBaseSchema)
            for employee in employees
        ],
    )


@account_router.get(
    "/{employee_id}", response_model=SingleEmployeeResponseSchema
)
async def get_employee_account(
    employee_id: str,
    have_permission: AuthJWT = Depends(
        EmployeeRoleChecker(EmployeeRole.MANAGE_EMPLOYEES)
    ),
):
    if not ObjectId.is_valid(employee_id):
        raise_unprocessable_value_exception(
            message="invalid employee id",
            location=["path parameter", "employee_id"],
        )
    employee = await controller.find_employee_by_id(id=employee_id)

    if not employee:
        raise_not_found_exception(
            message=f"employee with an id={employee_id} not found",
            location=["path parameter", "employee_id"],
        )

    return SingleEmployeeResponseSchema(
        success=True,
        employee=dict_to_model(model=EmployeeBaseSchema, dict_model=employee),
    )


# @account_router
# TODO: [patch] /change_password/{id}
# TODO: [get] /mine/change_info/{id}
# TODO: [patch] /deactivate_employee/{id}
# TODO: [patch] /activate_employee/{id}
