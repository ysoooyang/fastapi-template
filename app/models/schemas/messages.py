"""
错误消息常量定义

用于集中管理系统中的错误消息，便于将来支持多语言
"""

class ErrorMessages:
    """错误消息常量
    
    系统中所有错误消息的定义，按功能模块分组
    """
    # 通用错误消息
    UNKNOWN_ERROR = "服务器内部错误"
    PARAM_ERROR = "请求参数错误"
    
    # 认证相关错误消息
    INVALID_CREDENTIALS = "用户名或密码错误"
    USER_EXISTS = "该用户名已被使用"
    INVALID_TOKEN = "无效的认证凭据"
    USER_NOT_FOUND = "用户不存在"
    USER_INACTIVE = "用户未激活"
    
    # 权限相关错误消息
    PERMISSION_DENIED = "权限不足"
    ROLE_NOT_FOUND = "角色不存在"
    PERMISSION_NOT_FOUND = "权限不存在"
    
    # 数据相关错误消息
    DATA_NOT_FOUND = "数据不存在"
    DATA_ALREADY_EXISTS = "数据已存在"
    
    # 系统相关错误消息
    SYSTEM_ERROR = "系统错误"
    DATABASE_ERROR = "数据库操作失败"
    SERVICE_UNAVAILABLE = "服务不可用"
    
    # 第三方服务相关错误消息
    THIRD_PARTY_ERROR = "第三方服务错误"


class SuccessMessages:
    """成功消息常量
    
    系统中所有成功消息的定义，按功能模块分组
    """
    # 通用成功消息
    SUCCESS = "操作成功"
    
    # 认证相关成功消息
    LOGIN_SUCCESS = "登录成功"
    REGISTER_SUCCESS = "注册成功"
    TOKEN_VALID = "令牌有效"
    
    # 角色权限相关成功消息
    ROLE_CREATE_SUCCESS = "角色创建成功"
    ROLE_UPDATE_SUCCESS = "角色更新成功"
    ROLE_DELETE_SUCCESS = "角色删除成功"
    ROLE_ASSIGN_SUCCESS = "角色分配成功"
    PERMISSION_CREATE_SUCCESS = "权限创建成功"
    PERMISSION_UPDATE_SUCCESS = "权限更新成功"
    PERMISSION_DELETE_SUCCESS = "权限删除成功" 