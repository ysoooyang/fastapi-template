from typing import List, Optional, Callable, Any
import logging
from fastapi import Depends, HTTPException, status
from fastapi_permissions import Allow, Deny, Everyone, Authenticated, configure_permissions
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.domain.user import User
from app.utils.security import get_current_user
from app.utils.cache import async_cache

logger = logging.getLogger(__name__)

# 权限常量
class Permissions:
    """权限常量定义类
    
    包含系统中所有权限的常量定义，按功能模块分组
    """
    # 用户管理权限
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # 角色管理权限
    ROLE_CREATE = "role:create"
    ROLE_READ = "role:read"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"
    
    # 权限管理权限
    PERMISSION_CREATE = "permission:create"
    PERMISSION_READ = "permission:read"
    PERMISSION_UPDATE = "permission:update"
    PERMISSION_DELETE = "permission:delete"
    
    # 自动回复规则权限
    RULE_CREATE = "rule:create"
    RULE_READ = "rule:read"
    RULE_UPDATE = "rule:update"
    RULE_DELETE = "rule:delete"
    
    # 消息管理权限
    MESSAGE_CREATE = "message:create"
    MESSAGE_READ = "message:read"
    MESSAGE_UPDATE = "message:update"
    MESSAGE_DELETE = "message:delete"
    
    @classmethod
    def get_all_permissions(cls) -> List[str]:
        """获取所有权限列表
        
        Returns:
            List[str]: 所有权限的列表
        """
        return [p for p in dir(cls) if not p.startswith("_") and isinstance(getattr(cls, p), str)]


@async_cache("user_permissions", 300)  # 缓存5分钟
async def get_user_permissions(user: User) -> List[str]:
    """获取用户权限列表
    
    Args:
        user: 用户对象
        
    Returns:
        List[str]: 用户拥有的权限列表
    """
    try:
        if user.is_superuser:
            # 超级管理员拥有所有权限
            return Permissions.get_all_permissions()
        
        return user.get_permissions()
    except Exception as e:
        logger.error(f"获取用户权限失败: {e}")
        return []


async def get_active_principals(user: User = Depends(get_current_user)) -> List[str]:
    """获取用户权限主体
    
    Args:
        user: 用户对象
        
    Returns:
        List[str]: 用户的权限主体列表
    """
    try:
        if user.is_active:
            principals = [Everyone, Authenticated]
            user_permissions = await get_user_permissions(user)
            principals.extend(user_permissions)
            if user.is_superuser:
                principals.append("superuser")
            return principals
        return [Everyone]
    except Exception as e:
        logger.error(f"获取用户权限主体失败: {e}")
        return [Everyone]


async def check_permissions(required_permissions: List[str], user: User) -> bool:
    """检查用户是否拥有所有指定权限
    
    Args:
        required_permissions: 需要检查的权限列表
        user: 用户对象
        
    Returns:
        bool: 是否拥有所有指定权限
    """
    try:
        if user.is_superuser:
            return True
        
        user_permissions = await get_user_permissions(user)
        return all(perm in user_permissions for perm in required_permissions)
    except Exception as e:
        logger.error(f"权限检查失败: {e}")
        return False


def require_permissions(required_permissions: List[str]) -> Callable:
    """要求用户拥有指定权限
    
    Args:
        required_permissions: 需要的权限列表
        
    Returns:
        Callable: 权限检查依赖函数
    """
    async def dependency(user: User = Depends(get_current_user)) -> User:
        try:
            if not await check_permissions(required_permissions, user):
                logger.warning(f"用户 {user.username} (ID: {user.id}) 权限不足, 需要权限: {required_permissions}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"权限检查异常: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="权限检查失败"
            )
    
    return dependency 