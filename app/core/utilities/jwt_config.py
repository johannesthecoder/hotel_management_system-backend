from base64 import b64decode
from os import environ
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from .database import db
from ..constants.employee_roles import EmployeeRole
from ..error.exceptions import (
    raise_not_found_exception,
    raise_unauthorized_exception,
    raise_unknown_error_exception,
    raise_unprocessable_value_exception,
)


load_dotenv()


class JWTAuthSetting(BaseModel):
    authjwt_algorithm: str = environ.get("JWT_ALGORITHM")
    authjwt_decode_algorithms: list[str] = [environ.get("JWT_ALGORITHM")]
    authjwt_token_location: set = {"cookies", "headers"}
    authjwt_access_cookie_key: str = "access_token"
    authjwt_refresh_cookie_key: str = "refresh_token"
    authjwt_cookie_csrf_protect: bool = False
    authjwt_public_key: str = b64decode(environ.get("JWT_PUBLIC_KEY")).decode(
        "utf-8"
    )
    authjwt_private_key: str = b64decode(
        environ.get("JWT_PRIVATE_KEY")
    ).decode("utf-8")


@AuthJWT.load_config
def get_config():
    return JWTAuthSetting()


class EmployeeRoleChecker:
    def __init__(self, required_role: EmployeeRole):
        self.required_role = required_role.value

    async def __call__(self, Authorize: AuthJWT = Depends()) -> str:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()

        if not ObjectId.is_valid(user_id):
            raise_unprocessable_value_exception(
                message="invalid/incorrect access token content",
                location=["cookies", "refresh_token"],
            )

        user = await db["employees"].find_one(
            filter={"_id": ObjectId(user_id), "is_active": True}
        )

        if not user:
            raise_not_found_exception(
                message="user no longer exists or was deactivated",
                location=["cookies", "access_token"],
            )

        if not self.required_role in user["roles"]:
            raise_unauthorized_exception(
                message="user does not have access to this route",
                location=["cookies", "access_token"],
            )

        return user_id


async def require_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()

    if not ObjectId.is_valid(user_id):
        raise_unprocessable_value_exception(
            message="invalid/incorrect access token content",
            location=["cookies", "refresh_token"],
        )

    employee = await db["employees"].find_one(
        filter={"_id": ObjectId(user_id), "is_active": True}
    )
    customer = await db["customers"].find_one(
        filter={"_id": ObjectId(user_id), "is_active": True}
    )

    if not employee and not customer:
        raise_not_found_exception(
            message="user no longer exists or was deactivated",
            location=["cookies", "access_token"],
        )

    return user_id
