NOT_FOUND = "not found" # 404
METHOD_NOT_ALLOWED = "method not allowed" # 405
DUPLICATED_ENTRY = "duplicated entry" # 409
UNAUTHORIZED = "unauthorized" # 401 -> do not know who the user is
FORBIDDEN = "forbidden" # 403 -> this user does not have access to this
BAD_REQUEST = "bad request" # 400 -> incorrect formatting of request [eg. missing a field in request body, header, query]
UNPROCESSABLE_VALUE = "unprocessable value" # 422 -> correct formatting but can not be processed [eg. providing string in place of number]
TOO_MANY_REQUEST = "too many request" # 429
OPERATION_FAILED = "operation failed" #424
UNKNOWN_ERROR = "unknown error" # ??? -> we do not know what happened. most likely code=50?
INTERNAL_ERROR = "internal error" #500#
