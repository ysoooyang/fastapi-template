from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.domain.role import Role, Permission
from app.models.domain.user import User
from app.models.schemas.role import RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate
from app.utils.cache import async_cache, clear_cache

logger = logging.getLogger(__name__)

# 角色服务
class RoleService:
    @staticmethod
    @async_cache("roles", 3600)
    async def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """获取所有角色
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            List[Role]: 角色列表
        """
        try:
            return db.query(Role).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"获取角色列表失败: {e}")
            return []
    
    @staticmethod
    @async_cache("role", 3600)
    async def get_role(db: Session, role_id: int) -> Optional[Role]:
        """根据ID获取角色
        
        Args:
            db: 数据库会话
            role_id: 角色ID
            
        Returns:
            Optional[Role]: 角色对象，如果不存在则返回None
        """
        try:
            return db.query(Role).filter(Role.id == role_id).first()
        except SQLAlchemyError as e:
            logger.error(f"获取角色失败, ID: {role_id}, 错误: {e}")
            return None
    
    @staticmethod
    async def create_role(db: Session, role_create: RoleCreate) -> Optional[Role]:
        """创建角色
        
        Args:
            db: 数据库会话
            role_create: 角色创建模型
            
        Returns:
            Optional[Role]: 创建的角色对象，如果失败则返回None
        """
        try:
            # 创建角色
            db_role = Role(
                name=role_create.name,
                description=role_create.description
            )
            db.add(db_role)
            db.flush()
            
            # 添加权限
            if role_create.permissions:
                permissions = db.query(Permission).filter(Permission.id.in_(role_create.permissions)).all()
                db_role.permissions = permissions
            
            db.commit()
            db.refresh(db_role)
            
            # 清除缓存
            await clear_cache("roles:*")
            await clear_cache("role:*")
            await clear_cache("user_permissions:*")  # 清除用户权限缓存
            
            logger.info(f"角色创建成功: {db_role.name} (ID: {db_role.id})")
            return db_role
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"角色创建失败: {e}")
            return None
    
    @staticmethod
    async def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
        """更新角色
        
        Args:
            db: 数据库会话
            role_id: 角色ID
            role_update: 角色更新模型
            
        Returns:
            Optional[Role]: 更新后的角色对象，如果不存在则返回None
        """
        try:
            db_role = db.query(Role).filter(Role.id == role_id).first()
            if not db_role:
                logger.warning(f"角色不存在, ID: {role_id}")
                return None
            
            # 更新基本信息
            update_data = role_update.dict(exclude_unset=True)
            if "permissions" in update_data:
                permissions = update_data.pop("permissions")
                if permissions is not None:
                    db_role.permissions = db.query(Permission).filter(Permission.id.in_(permissions)).all()
            
            for key, value in update_data.items():
                setattr(db_role, key, value)
            
            db.commit()
            db.refresh(db_role)
            
            # 清除缓存
            await clear_cache("roles:*")
            await clear_cache("role:*")
            await clear_cache("user_permissions:*")  # 清除用户权限缓存
            
            logger.info(f"角色更新成功: {db_role.name} (ID: {db_role.id})")
            return db_role
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"角色更新失败, ID: {role_id}, 错误: {e}")
            return None
    
    @staticmethod
    async def delete_role(db: Session, role_id: int) -> bool:
        """删除角色
        
        Args:
            db: 数据库会话
            role_id: 角色ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            db_role = db.query(Role).filter(Role.id == role_id).first()
            if not db_role:
                logger.warning(f"角色不存在, ID: {role_id}")
                return False
            
            role_name = db_role.name
            db.delete(db_role)
            db.commit()
            
            # 清除缓存
            await clear_cache("roles:*")
            await clear_cache("role:*")
            await clear_cache("user_permissions:*")  # 清除用户权限缓存
            
            logger.info(f"角色删除成功: {role_name} (ID: {role_id})")
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"角色删除失败, ID: {role_id}, 错误: {e}")
            return False
    
    @staticmethod
    async def assign_user_roles(db: Session, user_id: int, role_ids: List[int]) -> Optional[User]:
        """为用户分配角色
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            role_ids: 角色ID列表
            
        Returns:
            Optional[User]: 更新后的用户对象，如果不存在则返回None
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"用户不存在, ID: {user_id}")
                return None
            
            roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
            user.roles = roles
            
            db.commit()
            db.refresh(user)
            
            # 清除用户权限缓存
            await clear_cache(f"user_permissions:*")
            
            logger.info(f"用户角色分配成功: 用户 {user.username} (ID: {user.id}), 角色IDs: {role_ids}")
            return user
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"用户角色分配失败, 用户ID: {user_id}, 错误: {e}")
            return None


# 权限服务
class PermissionService:
    @staticmethod
    @async_cache("permissions", 3600)
    async def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
        """获取所有权限
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            List[Permission]: 权限列表
        """
        try:
            return db.query(Permission).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"获取权限列表失败: {e}")
            return []
    
    @staticmethod
    @async_cache("permission", 3600)
    async def get_permission(db: Session, permission_id: int) -> Optional[Permission]:
        """根据ID获取权限
        
        Args:
            db: 数据库会话
            permission_id: 权限ID
            
        Returns:
            Optional[Permission]: 权限对象，如果不存在则返回None
        """
        try:
            return db.query(Permission).filter(Permission.id == permission_id).first()
        except SQLAlchemyError as e:
            logger.error(f"获取权限失败, ID: {permission_id}, 错误: {e}")
            return None
    
    @staticmethod
    async def create_permission(db: Session, permission_create: PermissionCreate) -> Optional[Permission]:
        """创建权限
        
        Args:
            db: 数据库会话
            permission_create: 权限创建模型
            
        Returns:
            Optional[Permission]: 创建的权限对象，如果失败则返回None
        """
        try:
            db_permission = Permission(
                name=permission_create.name,
                description=permission_create.description
            )
            db.add(db_permission)
            db.commit()
            db.refresh(db_permission)
            
            # 清除缓存
            await clear_cache("permissions:*")
            await clear_cache("permission:*")
            
            logger.info(f"权限创建成功: {db_permission.name} (ID: {db_permission.id})")
            return db_permission
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"权限创建失败: {e}")
            return None
    
    @staticmethod
    async def update_permission(db: Session, permission_id: int, permission_update: PermissionUpdate) -> Optional[Permission]:
        """更新权限
        
        Args:
            db: 数据库会话
            permission_id: 权限ID
            permission_update: 权限更新模型
            
        Returns:
            Optional[Permission]: 更新后的权限对象，如果不存在则返回None
        """
        try:
            db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
            if not db_permission:
                logger.warning(f"权限不存在, ID: {permission_id}")
                return None
            
            update_data = permission_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_permission, key, value)
            
            db.commit()
            db.refresh(db_permission)
            
            # 清除缓存
            await clear_cache("permissions:*")
            await clear_cache("permission:*")
            await clear_cache("user_permissions:*")  # 清除用户权限缓存
            
            logger.info(f"权限更新成功: {db_permission.name} (ID: {db_permission.id})")
            return db_permission
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"权限更新失败, ID: {permission_id}, 错误: {e}")
            return None
    
    @staticmethod
    async def delete_permission(db: Session, permission_id: int) -> bool:
        """删除权限
        
        Args:
            db: 数据库会话
            permission_id: 权限ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
            if not db_permission:
                logger.warning(f"权限不存在, ID: {permission_id}")
                return False
            
            permission_name = db_permission.name
            db.delete(db_permission)
            db.commit()
            
            # 清除缓存
            await clear_cache("permissions:*")
            await clear_cache("permission:*")
            await clear_cache("user_permissions:*")  # 清除用户权限缓存
            
            logger.info(f"权限删除成功: {permission_name} (ID: {permission_id})")
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"权限删除失败, ID: {permission_id}, 错误: {e}")
            return False 