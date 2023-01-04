from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi_jwt_auth.exceptions import AuthJWTException
from .core.models.error_response import ErrorSchema, ErrorResponseSchema
from .core.constants.error_type import (
    UNAUTHORIZED,
    NOT_FOUND,
    METHOD_NOT_ALLOWED,
    UNKNOWN_ERROR,
    UNPROCESSABLE_VALUE,
)
from .features.auth.routes import router as auth_router
from .features.account import employee_router
from .features.account import customer_router


api = FastAPI(responses={422: {"model": ErrorResponseSchema}})


@api.exception_handler(
    AuthJWTException,
)
def authjwt_exception_handler(request: Request, exception: AuthJWTException):
    return JSONResponse(
        status_code=exception.status_code,
        content=ErrorResponseSchema(
            success=False,
            errors=[
                ErrorSchema(
                    type=UNAUTHORIZED,
                    message=exception.message,
                    location=["cookies", "access_token"],
                )
            ],
        ).dict(),
    )


@api.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exception: StarletteHTTPException
):
    if type(exception.detail) == ErrorResponseSchema:
        return JSONResponse(
            status_code=exception.status_code,
            content=exception.detail.dict(),
        )

    if exception.status_code == 404:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(
                ErrorResponseSchema(
                    success=False,
                    errors=[
                        ErrorSchema(
                            type=NOT_FOUND,
                            message=f"this path/route[{request.url}] does not exist. double check you url",
                            location=["path"],
                        )
                    ],
                ).dict()
            ),
        )
    elif exception.status_code == 405:
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content=jsonable_encoder(
                ErrorResponseSchema(
                    success=False,
                    errors=[
                        ErrorSchema(
                            type=METHOD_NOT_ALLOWED,
                            message=f"this method [{request.method}] is not allowed for this route. try using an other method",
                            location=["path"],
                        )
                    ],
                ).dict()
            ),
        )

    return JSONResponse(
        status_code=exception.status_code,
        content=jsonable_encoder(
            ErrorResponseSchema(
                success=False,
                errors=[
                    ErrorSchema(
                        type=UNKNOWN_ERROR,
                        message=str(exception.detail),
                        location=[],
                    )
                ],
            ).dict()
        ),
    )


@api.exception_handler(RequestValidationError)
async def http_exception_handler(
    request: Request, exception: RequestValidationError
):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            ErrorResponseSchema(
                success=False,
                errors=[
                    ErrorSchema(
                        type=UNPROCESSABLE_VALUE,
                        message=error.get("msg"),
                        location=error.get("loc"),
                    )
                    for error in exception.errors()
                ],
            ).dict()
        ),
    )


api.include_router(auth_router, prefix="/auth")
api.include_router(employee_router, prefix="/account/employee")
api.include_router(customer_router, prefix="/account/customer")


@api.get("/api")
def root():
    return {
        "success": True,
        "message": "welcome to `hotel management system api`. ;)",
    }
