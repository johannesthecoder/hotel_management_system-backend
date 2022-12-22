from base64 import b64decode
from os import environ

from dotenv import load_dotenv
from pydantic import BaseModel


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
