from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.schemas.common import ResponseModel, ErrorCode

logger = logging.getLogger(__name__)

class APIException(Exception):
    """API异常基类
    
    自定义API异常，包含错误码和错误消息
    """
    def __init__(self, code: int, message: str, data: dict = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)


def add_exception_handlers(app: FastAPI) -> None:
    """添加全局异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """处理自定义API异常"""
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResponseModel.error(
                code=exc.code,
                msg=exc.message,
                data=exc.data
            ).dict()
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求参数验证错误"""
        errors = exc.errors()
        error_details = []
        
        for error in errors:
            error_details.append({
                "loc": error.get("loc", []),
                "msg": error.get("msg", ""),
                "type": error.get("type", "")
            })
        
        logger.warning(f"请求参数验证失败: {error_details}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResponseModel.error(
                code=ErrorCode.REQUEST_PARAM_ERROR,
                msg="请求参数错误",
                data=error_details
            ).dict()
        )
    
    @app.exception_handler(status.HTTP_401_UNAUTHORIZED)
    async def unauthorized_exception_handler(request: Request, exc: Exception):
        """处理未认证错误"""
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResponseModel.error(
                code=ErrorCode.INVALID_TOKEN,
                msg="无效的认证凭据",
                data=None
            ).dict()
        )
    
    @app.exception_handler(status.HTTP_404_NOT_FOUND)
    async def not_found_exception_handler(request: Request, exc: Exception):
        """处理资源不存在错误"""
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResponseModel.error(
                code=ErrorCode.USER_NOT_FOUND,
                msg="用户不存在",
                data=None
            ).dict()
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """处理数据库异常"""
        logger.error(f"数据库错误: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResponseModel.error(
                code=ErrorCode.SYSTEM_ERROR,
                msg="数据库操作失败"
            ).dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理通用异常"""
        logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResponseModel.error(
                code=ErrorCode.UNKNOWN_ERROR,
                msg="服务器内部错误"
            ).dict()
        ) 