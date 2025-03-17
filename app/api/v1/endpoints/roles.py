from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.domain.user import User
from app.models.schemas.role import Role, RoleCreate, RoleUpdate, Permission, PermissionCreate, PermissionUpdate, UserRoleAssign
from app.models.schemas.common import ResponseModel, ErrorCode
from app.models.schemas.messages import ErrorMessages, SuccessMessages
from app.services.role import RoleService, PermissionService
from app.utils.security import get_current_active_user
from app.utils.permissions import require_permissions, Permissions
from app.core.exceptions import APIException

router = APIRouter()

# 角色管理API
@router.get("/roles", response_model=ResponseModel[List[Role]], summary="获取所有角色")
async def get_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions([Permissions.ROLE_READ]))
):
    """
    获取所有角色列表
    """
    roles = await RoleService.get_roles(db, skip=skip, limit=limit)
    return ResponseModel.success(data=roles)


@router.get("/roles/{role_id}", response_model=ResponseModel[Role], summary="获取角色详情")
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions([Permissions.ROLE_READ]))
):
    """
    根据ID获取角色详情
    """
    role = await RoleService.get_role(db, role_id=role_id)
    if role is None:
        raise APIException(code=ErrorCode.ROLE_NOT_FOUND, message=ErrorMessages.ROLE_NOT_FOUND)
    return ResponseModel.success(data=role)


@router.post("/roles", 
    response_model=ResponseModel[Role], 
    status_code=status.HTTP_201_CREATED, 
    summary="创建角色",
    responses={
        201: {
            "description": "角色创建成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 0,
                        "msg": SuccessMessages.ROLE_CREATE_SUCCESS,
                        "data": {
                            "id": 1,
                            "name": "管理员",
                            "description": "系统管理员",
                            "permissions": []
                        }
                    }
                }
            }
        },
        400: {
            "description": "创建失败",
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.DATA_ALREADY_EXISTS,
                        "msg": ErrorMessages.DATA_ALREADY_EXISTS,
                        "data": None
                    }
                }
            }
        },
        403: {
            "description": "权限不足",
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.PERMISSION_DENIED,
                        "msg": ErrorMessages.PERMISSION_DENIED,
                        "data": None
                    }
                }
            }
        }
    }
)
async def create_role(
    role_create: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions([Permissions.ROLE_CREATE]))
):
    """
    创建新角色
    
    Args:
        role_create: 角色创建信息
        db: 数据库会话
        current_user: 当前用户（需要ROLE_CREATE权限）
        
    Returns:
        ResponseModel[Role]: 标准响应，包含创建的角色信息
        
    Raises:
        APIException: 创建角色失败时抛出异常
    """
    role = await RoleService.create_role(db=db, role_create=role_create)
    return ResponseModel.success(data=role, msg=SuccessMessages.ROLE_CREATE_SUCCESS)


@router.put("/roles/{role_id}", response_model=ResponseModel[Role], summary="更新角色")
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions([Permissions.ROLE_UPDATE]))
):
    """
    更新角色信息
    """
    role = await RoleService.update_role(db=db, role_id=role_id, role_update=role_update)
    if role is None:
        raise APIException(code=ErrorCode.ROLE_NOT_FOUND, message=ErrorMessages.ROLE_NOT_FOUND)
    return ResponseModel.success(data=role, msg=SuccessMessages.ROLE_UPDATE_SUCCESS)


@router.delete("/roles/{role_id}", response_model=ResponseModel[dict], status_code=status.HTTP_200_OK, summary="删除角色")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions([Permissions.ROLE_DELETE]))
):
    """
    删除角色
    """
    result = await RoleService.delete_role(db=db, role_id=role_id)
    if not result:
        raise APIException(code=ErrorCode.ROLE_NOT_FOUND, message=ErrorMessages.ROLE_NOT_FOUND)
    return ResponseModel.success(data={"status": "success"}, msg=SuccessMessages.ROLE_DELETE_SUCCESS)


@router.post("/users/{user_id}/roles", response_model=ResponseModel[dict], summary="为用户分配角色")
async def assign_user_roles(
    user_id: int,
    role_assign: UserRoleAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions([Permissions.USER_UPDATE, Permissions.ROLE_UPDATE]))
):
    """
    为用户分配角色
    """
    user = await RoleService.assign_user_roles(db=db, user_id=user_id, role_ids=role_assign.role_ids)
    if user is None:
        raise APIException(code=ErrorCode.USER_NOT_FOUND, message=ErrorMessages.USER_NOT_FOUND)
    return ResponseModel.success(data={"status": "success"}, msg=SuccessMessages.ROLE_ASSIGN_SUCCESS)


# 权限管理API
@router.get("/permissions", response_model=ResponseModel[List[Permission]], summary="获取所有权限")
async def get_permissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions([Permissions.PERMISSION_READ]))
):
    """
    获取所有权限列表
    """
    permissions = await PermissionService.get_permissions(db, skip=skip, limit=limit)
    return ResponseModel.success(data=permissions)


@router.get("/permissions/{permission_id}", response_model=ResponseModel[Permission], summary="获取权限详情")
async def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions([Permissions.PERMISSION_READ]))
):
    """
    根据ID获取权限详情
    """
    permission = await PermissionService.get_permission(db, permission_id=permission_id)
    if permission is None:
        raise APIException(code=ErrorCode.PERMISSION_NOT_FOUND, message=ErrorMessages.PERMISSION_NOT_FOUND)
    return ResponseModel.success(data=permission)


@router.post("/permissions", 
    response_model=ResponseModel[Permission], 
    status_code=status.HTTP_201_CREATED, 
    summary="创建权限",
    responses={
        201: {
            "description": "权限创建成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 0,
                        "msg": SuccessMessages.PERMISSION_CREATE_SUCCESS,
                        "data": {
                            "id": 1,
                            "name": "用户管理",
                            "code": "USER_MANAGE",
                            "description": "用户管理权限"
                        }
                    }
                }
            }
        },
        400: {
            "description": "创建失败",
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.DATA_ALREADY_EXISTS,
                        "msg": ErrorMessages.DATA_ALREADY_EXISTS,
                        "data": None
                    }
                }
            }
        },
        403: {
            "description": "权限不足",
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.PERMISSION_DENIED,
                        "msg": ErrorMessages.PERMISSION_DENIED,
                        "data": None
                    }
                }
            }
        }
    }
)
async def create_permission(
    permission_create: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions([Permissions.PERMISSION_CREATE]))
):
    """
    创建新权限
    
    Args:
        permission_create: 权限创建信息
        db: 数据库会话
        current_user: 当前用户（需要PERMISSION_CREATE权限）
        
    Returns:
        ResponseModel[Permission]: 标准响应，包含创建的权限信息
        
    Raises:
        APIException: 创建权限失败时抛出异常
    """
    permission = await PermissionService.create_permission(db=db, permission_create=permission_create)
    return ResponseModel.success(data=permission, msg=SuccessMessages.PERMISSION_CREATE_SUCCESS)


@router.put("/permissions/{permission_id}", response_model=ResponseModel[Permission], summary="更新权限")
async def update_permission(
    permission_id: int,
    permission_update: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions([Permissions.PERMISSION_UPDATE]))
):
    """
    更新权限信息
    """
    permission = await PermissionService.update_permission(db=db, permission_id=permission_id, permission_update=permission_update)
    if permission is None:
        raise APIException(code=ErrorCode.PERMISSION_NOT_FOUND, message=ErrorMessages.PERMISSION_NOT_FOUND)
    return ResponseModel.success(data=permission, msg=SuccessMessages.PERMISSION_UPDATE_SUCCESS)


@router.delete("/permissions/{permission_id}", response_model=ResponseModel[dict], status_code=status.HTTP_200_OK, summary="删除权限")
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions([Permissions.PERMISSION_DELETE]))
):
    """
    删除权限
    """
    result = await PermissionService.delete_permission(db=db, permission_id=permission_id)
    if not result:
        raise APIException(code=ErrorCode.PERMISSION_NOT_FOUND, message=ErrorMessages.PERMISSION_NOT_FOUND)
    return ResponseModel.success(data={"status": "success"}, msg=SuccessMessages.PERMISSION_DELETE_SUCCESS) 