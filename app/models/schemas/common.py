from typing import Generic, Optional, TypeVar, Dict, Any
from pydantic import BaseModel, Field

DataT = TypeVar('DataT')

class ErrorCode:
    """错误码常量定义
    
    系统中所有错误码的定义，按功能模块分组
    """
    # 通用错误码 (0-1000)
    SUCCESS = 0  # 成功
    UNKNOWN_ERROR = 1  # 未知错误
    PARAM_ERROR = 1000  # 参数错误
    
    # 认证相关错误码 (1001-1100)
    INVALID_CREDENTIALS = 1001  # 用户名或密码错误
    USER_EXISTS = 1002  # 用户已存在
    INVALID_TOKEN = 1003  # 无效的认证凭据
    USER_NOT_FOUND = 1004  # 用户不存在
    REQUEST_PARAM_ERROR = 1005  # 请求参数错误
    
    # 权限相关错误码 (1101-1200)
    PERMISSION_DENIED = 1101  # 权限不足
    ROLE_NOT_FOUND = 1102  # 角色不存在
    PERMISSION_NOT_FOUND = 1103  # 权限不存在
    
    # 数据相关错误码 (1201-1300)
    DATA_NOT_FOUND = 1201  # 数据不存在
    DATA_ALREADY_EXISTS = 1202  # 数据已存在
    
    # 系统相关错误码 (1301-1400)
    SYSTEM_ERROR = 1301  # 系统错误
    SERVICE_UNAVAILABLE = 1302  # 服务不可用
    
    # 第三方服务相关错误码 (1401-1500)
    THIRD_PARTY_ERROR = 1401  # 第三方服务错误


class ResponseModel(BaseModel, Generic[DataT]):
    """通用响应模式
    
    属性:
        code: 状态码，0表示成功，其他值表示错误
        msg: 响应消息
        data: 响应数据
    """
    code: int = Field(default=ErrorCode.SUCCESS, description="状态码，0表示成功，其他值表示错误")
    msg: str = Field(default="success", description="响应消息")
    data: Optional[DataT] = Field(default=None, description="响应数据")
    
    @classmethod
    def success(cls, data: Any = None, msg: str = "success") -> "ResponseModel":
        """成功响应
        
        Args:
            data: 响应数据
            msg: 响应消息
            
        Returns:
            ResponseModel: 成功响应对象
        """
        return cls(code=ErrorCode.SUCCESS, msg=msg, data=data)
    
    @classmethod
    def error(cls, code: int, msg: str, data: Any = None) -> "ResponseModel":
        """错误响应
        
        Args:
            code: 错误码
            msg: 错误消息
            data: 错误详情数据
            
        Returns:
            ResponseModel: 错误响应对象
        """
        return cls(code=code, msg=msg, data=data) 