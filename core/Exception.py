from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class BaseAPIException(HTTPException):
    """Base API exception class that extends FastAPI's HTTPException"""
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BadRequestException(BaseAPIException):
    """400 Bad Request Exception"""
    def __init__(
        self,
        detail: Any = "请求无效",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers)


class UnauthorizedException(BaseAPIException):
    """401 Unauthorized Exception"""
    def __init__(
        self,
        detail: Any = "未经授权",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers)


class ForbiddenException(BaseAPIException):
    """403 Forbidden Exception"""
    def __init__(
        self,
        detail: Any = "禁止访问",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers)


class NotFoundException(BaseAPIException):
    """404 Not Found Exception"""
    def __init__(
        self,
        detail: Any = "资源不存在",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers)


class InternalServerErrorException(BaseAPIException):
    """500 Internal Server Error Exception"""
    def __init__(
        self,
        detail: Any = "服务器内部错误",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail, headers=headers)


class DatabaseException(BaseAPIException):
    """Custom database exception"""
    def __init__(
        self,
        detail: Any = "数据库操作失败",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail, headers=headers)


class ValidationException(BaseAPIException):
    """Custom validation exception"""
    def __init__(
        self,
        detail: Any = "数据验证失败",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers)


