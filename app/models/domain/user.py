from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.utils.security import get_password_hash

class User(Base):
    """用户模型
    
    属性:
        id: 用户ID，主键
        username: 用户名，唯一
        email: 邮箱，唯一
        full_name: 用户全名
        hashed_password: 加密后的密码
        is_active: 是否激活
        is_superuser: 是否超级管理员
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # 关联关系
    roles = relationship("Role", secondary="user_role", back_populates="users")

    def set_password(self, password: str):
        """设置用户密码
        
        Args:
            password: 明文密码
        """
        self.hashed_password = get_password_hash(password)
        
    def get_permissions(self):
        """获取用户所有权限"""
        permissions = set()
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        return list(permissions) 