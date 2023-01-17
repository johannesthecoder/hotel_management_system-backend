from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, Query
from ....core.models.common_responses import UpdateResponseModel
from ....core.constants.regex import pin_code
from ....core.constants.employee_roles import EmployeeRole
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

customer_router = APIRouter()
customer_router.tags = ["Account - Customer"]


@customer_router.get("/me", response_model=models.SingleCustomerResponseModel)
async def get_me(current_user_id: AuthJWT = Depends(require_user)):
    customer = await controller.find_customer_by_id(id=current_user_id)

    if not customer:
        raise_unknown_error_exception(
            message="problem while getting customer details"
        )

    return models.SingleCustomerResponseModel(
        success=True,
        customer=dict_to_model(
            model=models.CustomerReadModel, dict_model=customer
        ),
    )


@customer_router.patch("/change_password", response_model=UpdateResponseModel)
async def change_my_password(
    old_password: str = Query(regex=pin_code),
    new_password: str = Query(regex=pin_code),
    current_user_id: AuthJWT = Depends(require_user),
):
    customer = await controller.find_customer_by_id(id=current_user_id)

    if not verify_password(
        password=old_password, hashed_password=customer["password"]
    ):
        raise_unauthorized_exception(
            message="old password is incorrect",
            location=["request body", "old_password"],
        )

    new_password = hash_password(password=new_password)

    result = await controller.update_customer_password(
        id=current_user_id,
        new_password=new_password,
        updated_by=current_user_id,
    )
    if not result:
        raise_operation_failed_exception(
            message="problem while changing password",
        )

    return UpdateResponseModel(success=True)


@customer_router.get("/", response_model=models.MultipleCustomerResponseModel)
async def get_customers(
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
    customers = await controller.find_many_customers(
        name=name,
        phone_number=phone_number,
        roles=[role.value for role in roles],
        is_active=is_active,
        limit=limit,
        skip=skip,
    )

    return models.MultipleCustomerResponseModel(
        success=True,
        customers=[
            dict_to_model(model=models.CustomerReadModel, dict_model=customer)
            for customer in customers
        ],
    )


@customer_router.get(
    "/{customer_id}", response_model=models.SingleCustomerResponseModel
)
async def get_customer(
    customer_id: str,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_EMPLOYEES)
    ),
):
    if not ObjectId.is_valid(customer_id):
        raise_unprocessable_value_exception(
            message=f"invalid customer_id={customer_id}",
            location=["path parameter", "customer_id"],
        )

    customer = await controller.find_customer_by_id(id=customer_id)

    if not customer:
        raise_not_found_exception(
            message=f"customer with id={customer} not found",
            location=["path parameter", "customer_id"],
        )

    return models.SingleCustomerResponseModel(
        success=True,
        customer=dict_to_model(
            model=models.CustomerReadModel, dict_model=customer
        ),
    )


@customer_router.patch(
    "/change_password/{customer_id}", response_model=UpdateResponseModel
)
async def change_customer_password(
    customer_id: str,
    old_password: str = Query(regex=pin_code),
    new_password: str = Query(regex=pin_code),
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_CUSTOMERS)
    ),
):
    if not ObjectId.is_valid(customer_id):
        raise_unprocessable_value_exception(
            message=f"invalid customer_id={customer_id}",
            location=["path parameter", "customer_id"],
        )

    customer = await controller.find_customer_by_id(id=customer_id)

    if not verify_password(
        password=old_password, hashed_password=customer["password"]
    ):
        raise_unauthorized_exception(
            message="old password is incorrect",
            location=["request body", "old_password"],
        )

    new_password = hash_password(password=new_password)

    result = await controller.update_customer_password(
        id=customer_id, new_password=new_password, updated_by=current_user_id
    )
    if not result:
        raise_operation_failed_exception(
            message="problem while changing password",
        )

    return UpdateResponseModel(success=True)


@customer_router.patch(
    "/deactivate/{customer_id}", response_model=UpdateResponseModel
)
async def deactivate_customer(
    customer_id: str,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_CUSTOMERS)
    ),
):
    if not ObjectId.is_valid(customer_id):
        raise_unprocessable_value_exception(
            message=f"invalid customer_id={customer_id}",
            location=["path parameter", "customer_id"],
        )

    result = await controller.deactivate_customer(
        id=customer_id, updated_by=current_user_id
    )

    if not result:
        raise_operation_failed_exception(
            message="problem while deactivating customer"
        )

    return UpdateResponseModel(success=True)


@customer_router.patch(
    "/activate/{customer_id}", response_model=UpdateResponseModel
)
async def activate_customer(
    customer_id: str,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_CUSTOMERS)
    ),
):
    if not ObjectId.is_valid(customer_id):
        raise_unprocessable_value_exception(
            message=f"invalid customer_id={customer_id}",
            location=["path parameter", "customer_id"],
        )

    result = await controller.activate_customer(
        id=customer_id, updated_by=current_user_id
    )

    if not result:
        raise_operation_failed_exception(
            message="problem while activating customer"
        )

    return UpdateResponseModel(success=True)


@customer_router.patch(
    "/update/{customer_id}", response_model=models.SingleCustomerResponseModel
)
async def update_customer_info(
    customer_id: str,
    updated_customer: models.CustomerUpdateModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_CUSTOMERS)
    ),
):
    if not ObjectId.is_valid(customer_id):
        raise_unprocessable_value_exception(
            message=f"invalid customer_id={customer_id}",
            location=["path parameter", "customer_id"],
        )

    if updated_customer.phone_number:
        if await controller.find_customer_by_phone_number(
            phone_number=updated_customer.phone_number
        ):
            raise_duplicated_entry_exception(
                message="customer with this phone number={updated_customer.phone_number} already exists",
                location=["request body", "phone_number"],
            )

    if updated_customer.first_name:
        updated_customer.first_name = updated_customer.first_name.lower()
    if updated_customer.last_name:
        updated_customer.last_name = updated_customer.last_name.lower()
    if updated_customer.nationality:
        updated_customer.nationality = updated_customer.nationality.lower()
    if updated_customer.passport_number:
        updated_customer.passport_number = (
            updated_customer.passport_number.lower()
        )

    result = await controller.update_customer_info(
        id=customer_id,
        updated_customer=model_to_dict_without_None(model=updated_customer),
        updated_by=current_user_id,
    )

    if not result:
        raise_operation_failed_exception(
            message="problem while updating customer info"
        )

    customer = await controller.find_customer_by_id(id=customer_id)

    return models.SingleCustomerResponseModel(
        success=True,
        customer=dict_to_model(
            model=models.CustomerReadModel, dict_model=customer
        ),
    )
