from pydantic import BaseModel
from typing import Any
class BaseResponse(BaseModel):
    code: int
    message: str
    data: Any


def success_response(message: str, data: Any = None):
    return BaseResponse(code=200, message=message, data=data)


def error_response(message: str):
    return BaseResponse(code=400, message=message, data=None)

