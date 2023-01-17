from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, Query
from ....core.constants.employee_roles import EmployeeRole
from ....core.models.common_responses import UpdateResponseModel
from ....core.constants.regex import pin_code
from ....core.utilities.converter import (
    dict_to_model,
    model_to_dict_without_None,
)
from ....core.utilities.password import hash_password, verify_password
from ....core.utilities.jwt_config import (
    AuthJWT,
    EmployeeRoleChecker,
    require_user,
)
from ....core.error.exceptions import (
    raise_duplicated_entry_exception,
    raise_not_found_exception,
    raise_operation_failed_exception,
    raise_unauthorized_exception,
    raise_unknown_error_exception,
    raise_unprocessable_value_exception,
)
from . import controller
from . import models

employee_router = APIRouter()
employee_router.tags = ["Account - Employee"]


@employee_router.get("/me", response_model=models.SingleEmployeeResponseModel)
async def get_me(current_user_id: AuthJWT = Depends(require_user)):
    employee = await controller.find_employee_by_id(id=current_user_id)

    if not employee:
        raise_unknown_error_exception(
            message="problem while getting employee details"
        )

    return models.SingleEmployeeResponseModel(
        success=True,
        employee=dict_to_model(
            model=models.EmployeeReadModel, dict_model=employee
        ),
    )


@employee_router.patch("/change_password", response_model=UpdateResponseModel)
async def change_my_password(
    old_password: str = Query(regex=pin_code),
    new_password: str = Query(regex=pin_code),
    current_user_id: AuthJWT = Depends(require_user),
):
    employee = await controller.find_employee_by_id(id=current_user_id)

    if not verify_password(
        password=old_password, hashed_password=employee["password"]
    ):
        raise_unauthorized_exception(
            message="old password is incorrect",
            location=["request body", "old_password"],
        )

    new_password = hash_password(password=new_password)

    result = await controller.update_employee_password(
        id=current_user_id,
        new_password=new_password,
        updated_by=current_user_id,
    )
    if not result:
        raise_operation_failed_exception(
            message="problem while changing password",
        )

    return UpdateResponseModel(success=True)


@employee_router.get("/", response_model=models.MultipleEmployeeResponseModel)
async def get_employees(
    roles: list[EmployeeRole] = Query(default=[]),
    name: str | None = None,
    phone_number: str | None = None,
    is_active: bool | None = None,
    limit: int | None = None,
    skip: int | None = None,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(EmployeeRole.VIEW_EMPLOYEES)
    ),
):
    employees = await controller.find_many_employees(
        name=name,
        phone_number=phone_number,
        roles=[role.value for role in roles],
        is_active=is_active,
        limit=limit,
        skip=skip,
    )

    return models.MultipleEmployeeResponseModel(
        success=True,
        employees=[
            dict_to_model(model=models.EmployeeReadModel, dict_model=employee)
            for employee in employees
        ],
    )


@employee_router.get(
    "/{employee_id}", response_model=models.SingleEmployeeResponseModel
)
async def get_employee(
    employee_id: str,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_EMPLOYEES)
    ),
):
    if not ObjectId.is_valid(employee_id):
        raise_unprocessable_value_exception(
            message=f"invalid employee_id={employee_id}",
            location=["path parameter", "employee_id"],
        )

    employee = await controller.find_employee_by_id(id=employee_id)

    if not employee:
        raise_not_found_exception(
            message=f"employee with id={employee} not found",
            location=["path parameter", "employee_id"],
        )

    return models.SingleEmployeeResponseModel(
        success=True,
        employee=dict_to_model(
            model=models.EmployeeReadModel, dict_model=employee
        ),
    )


@employee_router.patch(
    "/change_password/{employee_id}", response_model=UpdateResponseModel
)
async def change_employee_password(
    employee_id: str,
    old_password: str = Query(regex=pin_code),
    new_password: str = Query(regex=pin_code),
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_EMPLOYEES)
    ),
):
    if not ObjectId.is_valid(employee_id):
        raise_unprocessable_value_exception(
            message=f"invalid employee_id={employee_id}",
            location=["path parameter", "employee_id"],
        )

    employee = await controller.find_employee_by_id(id=employee_id)

    if not verify_password(
        password=old_password, hashed_password=employee["password"]
    ):
        raise_unauthorized_exception(
            message="old password is incorrect",
            location=["request body", "old_password"],
        )

    new_password = hash_password(password=new_password)

    result = await controller.update_employee_password(
        id=employee_id, new_password=new_password, updated_by=current_user_id
    )
    if not result:
        raise_operation_failed_exception(
            message="problem while changing password",
        )

    return UpdateResponseModel(success=True)


@employee_router.patch(
    "/deactivate/{employee_id}", response_model=UpdateResponseModel
)
async def deactivate_employee(
    employee_id: str,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_EMPLOYEES)
    ),
):
    if not ObjectId.is_valid(employee_id):
        raise_unprocessable_value_exception(
            message=f"invalid employee_id={employee_id}",
            location=["path parameter", "employee_id"],
        )

    result = await controller.deactivate_employee(
        id=employee_id, updated_by=current_user_id
    )

    if not result:
        raise_operation_failed_exception(
            message="problem while deactivating employee"
        )

    return UpdateResponseModel(success=True)


@employee_router.patch(
    "/activate/{employee_id}", response_model=UpdateResponseModel
)
async def activate_employee(
    employee_id: str,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_EMPLOYEES)
    ),
):
    if not ObjectId.is_valid(employee_id):
        raise_unprocessable_value_exception(
            message=f"invalid employee_id={employee_id}",
            location=["path parameter", "employee_id"],
        )

    result = await controller.activate_employee(
        id=employee_id, updated_by=current_user_id
    )

    if not result:
        raise_operation_failed_exception(
            message="problem while activating employee"
        )

    return UpdateResponseModel(success=True)


@employee_router.patch(
    "/add_roles/{employee_id}",
    response_model=models.SingleEmployeeResponseModel,
)
async def add_employee_roles(
    employee_id: str,
    roles: list[EmployeeRole],
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_EMPLOYEES)
    ),
):
    if not ObjectId.is_valid(employee_id):
        raise_unprocessable_value_exception(
            message=f"invalid employee_id={employee_id}",
            location=["path parameter", "employee_id"],
        )

    employee = await controller.find_employee_by_id(id=employee_id)

    roles = {role.value for role in roles} - set(employee["roles"])

    result = await controller.add_employee_roles(
        id=employee_id,
        roles=set(roles),
        updated_by=current_user_id,
    )

    if not result:
        raise_operation_failed_exception(
            message="problem while adding employee roles"
        )

    employee["roles"].extend(roles)

    return models.SingleEmployeeResponseModel(
        success=True,
        employee=dict_to_model(
            model=models.EmployeeReadModel, dict_model=employee
        ),
    )


@employee_router.patch(
    "/remove_roles/{employee_id}",
    response_model=models.SingleEmployeeResponseModel,
)
async def remove_employee_roles(
    employee_id: str,
    roles: list[EmployeeRole],
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_EMPLOYEES)
    ),
):
    if not ObjectId.is_valid(employee_id):
        raise_unprocessable_value_exception(
            message=f"invalid employee_id={employee_id}",
            location=["path parameter", "employee_id"],
        )

    result = await controller.remove_employee_roles(
        id=employee_id,
        roles=[role.value for role in roles],
        updated_by=current_user_id,
    )

    if not result:
        raise_operation_failed_exception(
            message="problem while adding employee roles"
        )

    employee = await controller.find_employee_by_id(id=employee_id)

    return models.SingleEmployeeResponseModel(
        success=True,
        employee=dict_to_model(
            model=models.EmployeeReadModel, dict_model=employee
        ),
    )


@employee_router.patch(
    "/update/{employee_id}", response_model=models.SingleEmployeeResponseModel
)
async def update_employee_info(
    employee_id: str,
    updated_employee: models.EmployeeUpdateModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_EMPLOYEES)
    ),
):
    if not ObjectId.is_valid(employee_id):
        raise_unprocessable_value_exception(
            message=f"invalid employee_id={employee_id}",
            location=["path parameter", "employee_id"],
        )

    if updated_employee.phone_number:
        if await controller.find_employee_by_phone_number(
            phone_number=updated_employee.phone_number
        ):
            raise_duplicated_entry_exception(
                message="employee with this phone number={updated_employee.phone_number} already exists",
                location=["request body", "phone_number"],
            )

    if updated_employee.first_name:
        updated_employee.first_name = updated_employee.first_name.lower()
    if updated_employee.last_name:
        updated_employee.last_name = updated_employee.last_name.lower()

    result = await controller.update_employee_info(
        id=employee_id,
        updated_employee=model_to_dict_without_None(model=updated_employee),
        updated_by=current_user_id,
    )

    if not result:
        raise_operation_failed_exception(
            message="problem while updating employee info"
        )

    employee = await controller.find_employee_by_id(id=employee_id)

    return models.SingleEmployeeResponseModel(
        success=True,
        employee=dict_to_model(
            model=models.EmployeeReadModel, dict_model=employee
        ),
    )
