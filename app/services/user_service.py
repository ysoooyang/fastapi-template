from typing import Optional
from sqlalchemy.orm import Session
from app.models.domain.user import User
from app.models.schemas.user import UserCreate
from app.utils.security import get_password_hash, verify_password

class UserService:
    """用户服务类
    
    处理用户相关的业务逻辑，如用户创建、认证等
    """
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """通过用户名获取用户
        
        Args:
            db: 数据库会话
            username: 用户名
            
        Returns:
            Optional[User]: 如果找到用户则返回用户对象，否则返回 None
        """
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        """创建新用户
        
        Args:
            db: 数据库会话
            user_in: 用户创建数据
            
        Returns:
            User: 创建的用户对象
        """
        user = User(
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            email=user_in.email,
            full_name=user_in.full_name
        )
        
        # 如果用户名是admin，则设置为超级管理员
        if user_in.username == "admin":
            user.is_superuser = True
            
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        """验证用户凭据
        
        Args:
            db: 数据库会话
            username: 用户名
            password: 密码
            
        Returns:
            Optional[User]: 如果验证成功则返回用户对象，否则返回 None
        """
        user = UserService.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user 