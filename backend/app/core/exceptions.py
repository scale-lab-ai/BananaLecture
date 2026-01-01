from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """应用程序基础异常类"""
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    """资源未找到异常"""
    def __init__(self, message: str = "Resource not found", details: Dict[str, Any] = None):
        super().__init__(message, 404, details)


class BadRequestException(AppException):
    """请求参数错误异常"""
    def __init__(self, message: str = "Bad request", details: Dict[str, Any] = None):
        super().__init__(message, 400, details)


class UnauthorizedException(AppException):
    """未授权异常"""
    def __init__(self, message: str = "Unauthorized", details: Dict[str, Any] = None):
        super().__init__(message, 401, details)


class ForbiddenException(AppException):
    """禁止访问异常"""
    def __init__(self, message: str = "Forbidden", details: Dict[str, Any] = None):
        super().__init__(message, 403, details)


class ConflictException(AppException):
    """资源冲突异常"""
    def __init__(self, message: str = "Conflict", details: Dict[str, Any] = None):
        super().__init__(message, 409, details)


class InternalServerException(AppException):
    """服务器内部错误异常"""
    def __init__(self, message: str = "Internal server error", details: Dict[str, Any] = None):
        super().__init__(message, 500, details)


def setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器"""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """处理应用程序自定义异常"""
        logger.error(f"AppException: {exc.message}, Details: {exc.details}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.message,
                    "details": exc.details,
                    "type": exc.__class__.__name__
                }
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """处理HTTP异常"""
        logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.detail,
                    "type": "HTTPException"
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求验证异常"""
        logger.error(f"RequestValidationError: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "message": "Validation error",
                    "details": exc.errors(),
                    "type": "RequestValidationError"
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理未捕获的异常"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "Internal server error",
                    "type": "InternalServerError"
                }
            }
        )