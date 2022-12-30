from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi_jwt_auth.exceptions import AuthJWTException
from .core.error.error_response import ErrorModel, ErrorResponseModel
from .core.constants.error_type import (
    UNAUTHORIZED,
    NOT_FOUND,
    METHOD_NOT_ALLOWED,
    UNKNOWN_ERROR,
    UNPROCESSABLE_VALUE,
)
from .features.auth.routes import router as auth_router


api = FastAPI(responses={422: {"model": ErrorResponseModel}})


@api.exception_handler(AuthJWTException,)
def authjwt_exception_handler(request: Request, exception: AuthJWTException):
    return JSONResponse(
        status_code=exception.status_code,
        content=ErrorResponseModel(
            success=False,
            errors=[
                ErrorModel(
                    type=UNAUTHORIZED,
                    message=exception.message,
                    location=["cookies", "access_token"],
                )
            ]
        ).dict()
    )


@api.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exception: StarletteHTTPException):
    if type(exception.detail) == ErrorResponseModel:
        return JSONResponse(
            status_code=exception.status_code,
            content=exception.detail.dict(),
        )

    if exception.status_code == 404:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(
                ErrorResponseModel(
                    success=False,
                    errors=[
                        ErrorModel(
                            type=NOT_FOUND,
                            message=f"this path/route[{request.url}] does not exist. double check you url",
                            location=["path"],
                        )
                    ]
                ).dict()
            )
        )
    elif exception.status_code == 405:
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content=jsonable_encoder(
                ErrorResponseModel(
                    success=False,
                    errors=[
                        ErrorModel(
                            type=METHOD_NOT_ALLOWED,
                            message=f"this method [{request.method}] is not allowed for this route. try using an other method",
                            location=["path"],
                        )
                    ]
                ).dict()
            )
        )

    return JSONResponse(
        status_code=exception.status_code,
        content=jsonable_encoder(
            ErrorResponseModel(
                success=False,
                errors=[
                    ErrorModel(
                        type=UNKNOWN_ERROR,
                        message=str(exception.detail),
                        location=[],
                    )
                ]
            ).dict()
        )
    )


@api.exception_handler(RequestValidationError)
async def http_exception_handler(request: Request, exception: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            ErrorResponseModel(
                success=False,
                errors=[
                    ErrorModel(
                        type=UNPROCESSABLE_VALUE,
                        message=error.get("msg"),
                        location=error.get("loc"),
                    ) for error in exception.errors()
                ]
            ).dict()
        )
    )


api.include_router(auth_router, prefix="/auth")


@api.get("/api")
def root():
    return {
        "success": True, "message": "welcome to `hotel management system api`. ;)"
    }
