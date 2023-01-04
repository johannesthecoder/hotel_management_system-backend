from os import environ
from datetime import datetime, timedelta
from re import match
from bson.objectid import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, Response, status, Depends
from ...core.utilities.converter import dict_to_model
from ...core.utilities.password import hash_password, verify_password
from ...core.utilities.jwt_config import AuthJWT, require_user
from ...core.constants.regex import pin_code
from ...core.error.exceptions import (
    raise_bad_request_exception, raise_duplicated_entry_exception,
    raise_not_found_exception, raise_operation_failed_exception,
    raise_unauthorized_exception, raise_unprocessable_value_exception
)
from .controller import (
    employee_exist, insert_employee, find_employee_by_phone_number, find_employee_by_id, update_employee_password,
)
from .models import (
    ChangePasswordResponseSchema, CreateEmployeeSchema,  CreateUserResponseSchema, LogoutResponseSchema, UserType,
    LoginUserSchema, LoginUserResponseSchema, UserResponseSchema,
    RefreshTokenResponseSchema
)

load_dotenv()
router = APIRouter()
employee_router = APIRouter()
employee_router.tags = ["Auth"]

# --------------->]  [<---------------
# TODO: add customer route.
# :customer can order food from rooms
# :customer can see there bill with details
# : and some other functionalities ...
# timing [for the 2 version of this system]
customer_router = APIRouter()
customer_router.tags = ["customer"]
# --------------->]  [<---------------

ACCESS_TOKEN_EXPIRES_IN = int(environ.get("ACCESS_TOKEN_EXPIRES_IN", "120"))
REFRESH_TOKEN_EXPIRES_IN = int(environ.get("REFRESH_TOKEN_EXPIRES_IN", "600"))


@employee_router.post("/register", status_code=status.HTTP_201_CREATED, response_model=CreateUserResponseSchema)
async def register_employee(payload: CreateEmployeeSchema):
    if await employee_exist(phone_number=payload.phone_number):
        raise_duplicated_entry_exception(
            message="employee with this phone number already exists. try logging in.",
            location=["request body", "phone_number"],
        )

    payload.first_name = payload.first_name.lower()
    payload.last_name = payload.last_name.lower() if payload.last_name else None
    payload.password = hash_password(payload.password)
    payload.created_at = datetime.utcnow()
    payload.updated_at = datetime.utcnow()

    if await insert_employee(employee=payload.dict()):
        inserted_employee = await find_employee_by_phone_number(phone_number=payload.phone_number)
        return CreateUserResponseSchema(
            success=True,
            user=dict_to_model(
                dict_model={"user_type": UserType.EMPLOYEE, **inserted_employee}, model=UserResponseSchema
            )
        )

    raise_operation_failed_exception(
        message="unable to finish employee registration.",
        location=["unknown"]
    )


@employee_router.post("/login", status_code=status.HTTP_201_CREATED, response_model=LoginUserResponseSchema)
async def login_employee(payload: LoginUserSchema, response: Response, Authorize: AuthJWT = Depends()):
    employee = await find_employee_by_phone_number(phone_number=payload.phone_number)

    if not employee:
        raise_not_found_exception(
            message="no employee with this phone number.",
            location=["request body", "phone_number"]
        )

    if not employee["is_active"]:
        raise_unauthorized_exception(
            message="this user is deactivated",
            location=["request body", "phone_number"]
        )

    if not verify_password(password=payload.password, hashed_password=employee["password"]):
        raise_not_found_exception(
            message="invalid/incorrect phone number or password",
            location=["request body", "password/phone_number"]
        )

    employee = dict_to_model(
        dict_model={"user_type": UserType.EMPLOYEE, **employee}, model=UserResponseSchema
    )

    access_token = Authorize.create_access_token(
        subject=str(employee.id), expires_time=timedelta(
            minutes=ACCESS_TOKEN_EXPIRES_IN
        )
    )
    refresh_token = Authorize.create_refresh_token(
        subject=str(employee.id), expires_time=timedelta(
            minutes=REFRESH_TOKEN_EXPIRES_IN
        )
    )
    response.set_cookie(
        'access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax'
    )
    response.set_cookie(
        'refresh_token', refresh_token,
        REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN *
        60, '/', None, False, True, 'lax'
    )
    response.set_cookie(
        'logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax'
    )

    return LoginUserResponseSchema(
        success=True,
        user=employee,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@employee_router.get("/refresh_token", response_model=RefreshTokenResponseSchema)
async def refresh_employee_token(response: Response, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()
        user_id = Authorize.get_jwt_subject()

        if not user_id:
            raise_unauthorized_exception(
                message="invalid/incorrect access token.",
                location=["cookies", "refresh_token"]
            )

        if not ObjectId.is_valid(user_id):
            raise_unprocessable_value_exception(
                message="invalid/incorrect access token content",
                location=["cookies", "refresh_token"]
            )

        employee = await find_employee_by_id(id=user_id)

        if not employee:
            raise_not_found_exception(
                message="this user no longer exists",
                location=["cookies", "access_token"]
            )

        if not employee["is_active"]:
            raise_unauthorized_exception(
                message="this user is deactivated",
                location=["cookies", "access_token"]
            ),

        access_token = Authorize.create_access_token(
            subject=str(employee["_id"]), expires_time=timedelta(
                minutes=ACCESS_TOKEN_EXPIRES_IN
            )
        )
    except Exception as e:
        error = e.__class__.__name__

        if error == "MissingTokenError":
            raise_bad_request_exception(
                message="refresh token was not provided.",
                location=["cookies", "refresh_token"],
            )

        if not error == "HTTPException":
            raise e

        raise_bad_request_exception(
            message=error,
            location=["unknown"],
        )

    response.set_cookie(
        'access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax'
    )
    response.set_cookie(
        'logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax'
    )

    return RefreshTokenResponseSchema(
        success=True,
        access_token=access_token,
    )


@employee_router.patch("/change_password", response_model=ChangePasswordResponseSchema)
async def change_employee_password(old_password: str, new_password: str, user_id: AuthJWT = Depends(require_user)):
    if not match(pin_code, new_password):
        raise_unprocessable_value_exception(
            message="invalid/incorrect new password. should contain minimum of 5 and maximum of 15 digits",
            location=["request body", "new_password"]
        )

    employee = await find_employee_by_id(id=user_id)

    if not verify_password(password=old_password, hashed_password=employee["password"]):
        raise_unauthorized_exception(
            message="old password is incorrect",
            location=["request body", "old_password"]
        )

    new_password = hash_password(password=new_password)

    if not await update_employee_password(id=employee["_id"], new_password=new_password):
        raise_operation_failed_exception(
            message="could not update password",
            location=["unknown"]
        )

    return ChangePasswordResponseSchema(
        success=True,
    )


@employee_router.get('/logout', status_code=status.HTTP_200_OK, response_model=LogoutResponseSchema)
def logout(response: Response, Authorize: AuthJWT = Depends(), user_id: str = Depends(require_user)):
    Authorize.unset_jwt_cookies()
    response.set_cookie('logged_in', '', -1)

    return LogoutResponseSchema(success=True)


router.include_router(employee_router, prefix="/employee")
