from typing import Optional
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    """登录请求模式
    
    属性:
        username: 用户名
        password: 密码
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="用户名",
        example="john_doe"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="密码",
        example="password123"
    )

class Token(BaseModel):
    """访问令牌模式
    
    属性:
        access_token: JWT访问令牌
        token_type: 令牌类型，固定为"bearer"
    """
    access_token: str = Field(
        ...,
        description="JWT访问令牌",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
    )
    token_type: str = Field(
        default="bearer",
        description="令牌类型",
        example="bearer"
    )

class TokenPayload(BaseModel):
    """令牌载荷模式
    
    属性:
        sub: 用户ID
    """
    sub: Optional[int] = Field(
        default=None,
        description="用户ID",
        example=1
    ) 