from typing import List, Optional
from pydantic import BaseModel

# 权限模型
class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    name: Optional[str] = None


class Permission(PermissionBase):
    id: int
    
    class Config:
        from_attributes = True


# 角色模型
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permissions: Optional[List[int]] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[int]] = None


class Role(RoleBase):
    id: int
    permissions: List[Permission] = []
    
    class Config:
        from_attributes = True


# 用户角色分配
class UserRoleAssign(BaseModel):
    role_ids: List[int] 