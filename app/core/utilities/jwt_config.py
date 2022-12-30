from base64 import b64decode
from os import environ
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT

from app.core.error.exceptions import raise_not_found_exception, raise_unauthorized_exception, raise_unprocessable_value_exception
from .database import db


load_dotenv()


class JWTAuthSetting(BaseModel):
    authjwt_algorithm: str = environ.get("JWT_ALGORITHM")
    authjwt_decode_algorithms: list[str] = [environ.get("JWT_ALGORITHM")]
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_public_key: str = b64decode(
        environ.get("JWT_PUBLIC_KEY")
    ).decode('utf-8')
    authjwt_private_key: str = b64decode(
        environ.get("JWT_PRIVATE_KEY")
    ).decode('utf-8')


@AuthJWT.load_config
def get_config():
    return JWTAuthSetting()


async def require_user(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()

        if not ObjectId.is_valid(user_id):
            raise_unprocessable_value_exception(
                message="invalid/incorrect access token content",
                location=["cookies", "refresh_token"]
            )

        user = await db["employees"].find_one(filter={"_id": ObjectId(user_id)})

        if not user:
            raise_not_found_exception(
                message="user no longer exists",
                location=["cookies", "access_token"]
            )

        if not user["is_active"]:
            raise_unauthorized_exception(
                message="this user is deactivated",
                location=["cookies", "access_token"]
            )

    except Exception as e:
        error = e.__class__.__name__

        if error == "MissingTokenError":
            raise_unauthorized_exception(
                message="user is not logged in",
                location=["cookies", "access_token"]
            )
        if error == "UserNotFound":
            raise_unauthorized_exception(
                message="user no longer exists",
                location=["cookies", "access_token"]
            )

        raise_unauthorized_exception(
            message="token is invalid or expired",
            location=["cookies", "access_token"]
        )

        pass

    return user_id
