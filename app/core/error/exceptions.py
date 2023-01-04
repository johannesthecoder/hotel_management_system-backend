from fastapi.exceptions import HTTPException
from fastapi import status

from ..constants.error_type import (
    NOT_FOUND,
    DUPLICATED_ENTRY,
    UNAUTHORIZED,
    FORBIDDEN,
    BAD_REQUEST,
    UNPROCESSABLE_VALUE,
    TOO_MANY_REQUEST,
    OPERATION_FAILED,
    UNKNOWN_ERROR,
    INTERNAL_ERROR,

)
from ..models.error_response import ErrorSchema, ErrorResponseSchema


def custom_http_exception_raiser(http_status, type: str, message: str, location: list[str]):
    raise HTTPException(
        status_code=http_status,
        detail=ErrorResponseSchema(
            success=False,
            errors=[
                ErrorSchema(
                    type=type,
                    message=message,
                    location=location,
                )
            ]
        )
    )


def raise_not_found_exception(message: str, location: list[str] = []):
    custom_http_exception_raiser(
        http_status=status.HTTP_404_NOT_FOUND,
        type=NOT_FOUND,
        message=message,
        location=location
    )


def raise_duplicated_entry_exception(message: str, location: list[str] = []):
    custom_http_exception_raiser(
        http_status=status.HTTP_409_CONFLICT,
        type=DUPLICATED_ENTRY,
        message=message,
        location=location
    )


def raise_unauthorized_exception(message: str, location: list[str] = []):
    custom_http_exception_raiser(
        http_status=status.HTTP_401_UNAUTHORIZED,
        type=UNAUTHORIZED,
        message=message,
        location=location
    )


def raise_forbidden_exception(message: str, location: list[str] = []):
    custom_http_exception_raiser(
        http_status=status.HTTP_403_FORBIDDEN,
        type=FORBIDDEN,
        message=message,
        location=location
    )


def raise_bad_request_exception(message: str, location: list[str] = []):
    custom_http_exception_raiser(
        http_status=status.HTTP_400_BAD_REQUEST,
        type=BAD_REQUEST,
        message=message,
        location=location
    )


def raise_unprocessable_value_exception(message: str, location: list[str] = []):
    custom_http_exception_raiser(
        http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        type=UNPROCESSABLE_VALUE,
        message=message,
        location=location
    )


def raise_too_many_request_exception(message: str, location: list[str] = []):
    custom_http_exception_raiser(
        http_status=status.HTTP_429_TOO_MANY_REQUESTS,
        type=TOO_MANY_REQUEST,
        message=message,
        location=location
    )


def raise_operation_failed_exception(message: str, location: list[str] = []):
    custom_http_exception_raiser(
        http_status=status.HTTP_424_FAILED_DEPENDENCY,
        type=OPERATION_FAILED,
        message=message,
        location=location
    )


def raise_unknown_error_exception(message: str, location: list[str] = []):
    custom_http_exception_raiser(
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        type=UNKNOWN_ERROR,
        message=message,
        location=location
    )


def raise_internal_error_exception(message: str, location: list[str] = []):
    custom_http_exception_raiser(
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        type=INTERNAL_ERROR,
        message=message,
        location=location
    )
