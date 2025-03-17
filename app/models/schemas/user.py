from pydantic import BaseModel, Field

class UserBase(BaseModel):
    """用户基础模式
    
    属性:
        username: 用户名
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern="^[a-zA-Z0-9_-]+$",
        description="用户名，只能包含字母、数字、下划线和连字符",
        example="john_doe"
    )

class UserCreate(UserBase):
    """用户创建模式
    
    属性:
        username: 用户名
        password: 密码
        email: 邮箱
        full_name: 用户全名
    """
    password: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="密码，长度在6-20个字符之间",
        example="password123"
    )
    email: str = Field(
        ...,
        description="邮箱地址",
        example="user@example.com",
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )
    full_name: str = Field(
        None,
        description="用户全名",
        example="John Doe"
    )

class User(UserBase):
    """用户模式
    
    属性:
        id: 用户ID
        username: 用户名
    """
    id: int = Field(..., description="用户ID", example=1)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe"
            }
        } 