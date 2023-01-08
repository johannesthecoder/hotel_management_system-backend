from os import environ
from datetime import timedelta
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Response, status, Depends, Query
from ...core.constants.employee_roles import EmployeeRole
from ...core.constants import regex
from ...core.utilities.converter import dict_to_model
from ...core.utilities.password import hash_password, verify_password
from ...core.utilities.jwt_config import (
    AuthJWT,
    EmployeeRoleChecker,
    require_user,
)
from ...core.error.exceptions import (
    raise_duplicated_entry_exception,
    raise_not_found_exception,
    raise_operation_failed_exception,
    raise_unauthorized_exception,
    raise_unprocessable_value_exception,
)
from ..account.employee import models as employee_model
from ..account.employee import controller as employee_controller
from ..account.customer import models as customer_model
from ..account.customer import controller as customer_controller
from . import models

load_dotenv()
auth_router = APIRouter()
employee_auth_router = APIRouter()
customer_auth_router = APIRouter()
auth_router.tags = ["Auth"]


ACCESS_TOKEN_EXPIRES_IN = int(environ.get("ACCESS_TOKEN_EXPIRES_IN", "120"))
REFRESH_TOKEN_EXPIRES_IN = int(environ.get("REFRESH_TOKEN_EXPIRES_IN", "600"))


@employee_auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=employee_model.SingleEmployeeResponseModel,
)
async def register_employee(
    new_employee: employee_model.EmployeeBaseModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(EmployeeRole.MANAGE_EMPLOYEES)
    ),
):
    if await employee_controller.find_employee_by_phone_number(
        phone_number=new_employee.phone_number
    ):
        raise_duplicated_entry_exception(
            message=f"employee with this phone number={new_employee.phone_number} already exists. try logging in.",
            location=["request body", "phone_number"],
        )

    new_employee.first_name = new_employee.first_name.lower()
    new_employee.last_name = (
        new_employee.last_name.lower() if new_employee.last_name else None
    )
    new_employee.password = hash_password(new_employee.password)

    if await employee_controller.create_employee(
        new_employee={**new_employee.dict()}, create_by=current_user_id
    ):
        inserted_employee = (
            await employee_controller.find_employee_by_phone_number(
                phone_number=new_employee.phone_number
            )
        )

        return employee_model.SingleEmployeeResponseModel(
            success=True,
            employee=dict_to_model(
                model=employee_model.EmployeeReadModel,
                dict_model=inserted_employee,
            ),
        )

    raise_operation_failed_exception(
        message="problem while registering employee.",
    )


@employee_auth_router.post(
    "/login",
    status_code=status.HTTP_201_CREATED,
    response_model=models.EmployeeLoginResponseModel,
)
async def login_employee(
    response: Response,
    phone_number: str = Query(regex=regex.phone_number),
    password: str = Query(regex=regex.pin_code),
    Authorize: AuthJWT = Depends(),
):
    employee = await employee_controller.find_employee_by_phone_number(
        phone_number=phone_number
    )
    employee["id"] = str(employee["_id"])

    if not employee:
        raise_not_found_exception(
            message="no employee with this phone number.",
            location=["request body", "phone_number"],
        )

    if not employee["is_active"]:
        raise_unauthorized_exception(
            message="this user is deactivated",
            location=["request body", "phone_number"],
        )

    if not verify_password(
        password=password, hashed_password=employee["password"]
    ):
        raise_not_found_exception(
            message="invalid/incorrect phone number or password",
            location=["request body", "password/phone_number"],
        )

    access_token = Authorize.create_access_token(
        subject=str(employee["id"]),
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )
    refresh_token = Authorize.create_refresh_token(
        subject=str(employee["id"]),
        expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN),
    )
    response.set_cookie(
        "access_token",
        access_token,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        REFRESH_TOKEN_EXPIRES_IN * 60,
        REFRESH_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "logged_in",
        "True",
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        False,
        "lax",
    )

    return models.EmployeeLoginResponseModel(
        success=True,
        employee=dict_to_model(
            model=employee_model.EmployeeReadModel, dict_model=employee
        ),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@employee_auth_router.get(
    "/refresh_token", response_model=models.RefreshTokenResponseModel
)
async def refresh_employee_token(
    response: Response, Authorize: AuthJWT = Depends()
):
    Authorize.jwt_refresh_token_required()
    employee_id = Authorize.get_jwt_subject()

    if not employee_id:
        raise_unauthorized_exception(
            message="invalid/incorrect access token.",
            location=["cookies", "refresh_token"],
        )

    if not ObjectId.is_valid(employee_id):
        raise_unprocessable_value_exception(
            message="invalid/incorrect access token content",
            location=["cookies", "refresh_token"],
        )

    employee = await employee_controller.find_employee_by_id(id=employee_id)

    if not employee:
        raise_not_found_exception(
            message="this employee no longer exists",
            location=["cookies", "access_token"],
        )

    if not employee["is_active"]:
        raise_unauthorized_exception(
            message="this employee is deactivated",
            location=["cookies", "access_token"],
        ),

    access_token = Authorize.create_access_token(
        subject=str(employee["_id"]),
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )

    response.set_cookie(
        "access_token",
        access_token,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "logged_in",
        "True",
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        False,
        "lax",
    )

    return models.RefreshTokenResponseModel(
        success=True,
        access_token=access_token,
    )


@employee_auth_router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=models.LogoutResponseModel,
)
def logout(
    response: Response,
    Authorize: AuthJWT = Depends(),
    employee_id: str = Depends(require_user),
):
    Authorize.unset_jwt_cookies()
    response.set_cookie("logged_in", "", -1)

    return models.LogoutResponseModel(success=True)


@customer_auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=customer_model.SingleCustomerResponseModel,
)
async def register_customer(
    new_customer: customer_model.CustomerBaseModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(EmployeeRole.MANAGE_EMPLOYEES)
    ),
):
    if await customer_controller.find_customer_by_phone_number(
        phone_number=new_customer.phone_number
    ):
        raise_duplicated_entry_exception(
            message=f"customer with this phone number={new_customer.phone_number} already exists. try logging in.",
            location=["request body", "phone_number"],
        )

    new_customer.first_name = new_customer.first_name.lower()
    new_customer.last_name = (
        new_customer.last_name.lower() if new_customer.last_name else None
    )
    new_customer.nationality = new_customer.nationality.lower()
    new_customer.passport_number = new_customer.passport_number.lower()
    new_customer.password = hash_password(new_customer.password)

    if await customer_controller.create_customer(
        new_customer={**new_customer.dict()}, create_by=current_user_id
    ):
        inserted_customer = (
            await customer_controller.find_customer_by_phone_number(
                phone_number=new_customer.phone_number
            )
        )

        return customer_model.SingleCustomerResponseModel(
            success=True,
            customer=dict_to_model(
                model=customer_model.CustomerReadModel,
                dict_model=inserted_customer,
            ),
        )

    raise_operation_failed_exception(
        message="problem while registering customer.",
    )


@customer_auth_router.post(
    "/login",
    status_code=status.HTTP_201_CREATED,
    response_model=models.CustomerLoginResponseModel,
)
async def login_customer(
    response: Response,
    phone_number: str = Query(regex=regex.phone_number),
    password: str = Query(regex=regex.pin_code),
    Authorize: AuthJWT = Depends(),
):
    customer = await customer_controller.find_customer_by_phone_number(
        phone_number=phone_number
    )
    customer["id"] = customer["_id"]

    if not customer:
        raise_not_found_exception(
            message="no customer with this phone number.",
            location=["request body", "phone_number"],
        )

    if not customer["is_active"]:
        raise_unauthorized_exception(
            message="this user is deactivated",
            location=["request body", "phone_number"],
        )

    if not verify_password(
        password=password, hashed_password=customer["password"]
    ):
        raise_not_found_exception(
            message="invalid/incorrect phone number or password",
            location=["request body", "password/phone_number"],
        )

    access_token = Authorize.create_access_token(
        subject=str(customer["id"]),
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )
    refresh_token = Authorize.create_refresh_token(
        subject=str(customer["id"]),
        expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN),
    )
    response.set_cookie(
        "access_token",
        access_token,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        REFRESH_TOKEN_EXPIRES_IN * 60,
        REFRESH_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "logged_in",
        "True",
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        False,
        "lax",
    )

    return models.CustomerLoginResponseModel(
        success=True,
        customer=dict_to_model(
            model=customer_model.CustomerReadModel, dict_model=customer
        ),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@customer_auth_router.get(
    "/refresh_token", response_model=models.RefreshTokenResponseModel
)
async def refresh_customer_token(
    response: Response, Authorize: AuthJWT = Depends()
):
    Authorize.jwt_refresh_token_required()
    customer_id = Authorize.get_jwt_subject()

    if not customer_id:
        raise_unauthorized_exception(
            message="invalid/incorrect access token.",
            location=["cookies", "refresh_token"],
        )

    if not ObjectId.is_valid(customer_id):
        raise_unprocessable_value_exception(
            message="invalid/incorrect access token content",
            location=["cookies", "refresh_token"],
        )

    customer = await customer_controller.find_customer_by_id(id=customer_id)

    if not customer:
        raise_not_found_exception(
            message="this customer no longer exists",
            location=["cookies", "access_token"],
        )

    if not customer["is_active"]:
        raise_unauthorized_exception(
            message="this customer is deactivated",
            location=["cookies", "access_token"],
        ),

    access_token = Authorize.create_access_token(
        subject=str(customer["_id"]),
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )

    response.set_cookie(
        "access_token",
        access_token,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "logged_in",
        "True",
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        False,
        "lax",
    )

    return models.RefreshTokenResponseModel(
        success=True,
        access_token=access_token,
    )


@customer_auth_router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=models.LogoutResponseModel,
)
def logout(
    response: Response,
    Authorize: AuthJWT = Depends(),
    customer_id: str = Depends(require_user),
):
    Authorize.unset_jwt_cookies()
    response.set_cookie("logged_in", "", -1)

    return models.LogoutResponseModel(success=True)


auth_router.include_router(employee_auth_router, prefix="/employee")
auth_router.include_router(customer_auth_router, prefix="/customer")
