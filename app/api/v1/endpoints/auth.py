from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.models.domain.user import User
from app.models.schemas.user import User as UserSchema, UserCreate
from app.models.schemas.token import Token, LoginRequest
from app.models.schemas.common import ResponseModel, ErrorCode
from app.models.schemas.messages import ErrorMessages, SuccessMessages
from app.utils.security import create_access_token
from app.services.user_service import UserService
from app.core.exceptions import APIException

router = APIRouter()

@router.post(
    "/login",
    response_model=ResponseModel[Token],
    status_code=status.HTTP_200_OK,
    summary="用户登录",
    description="使用用户名和密码登录，获取访问令牌。用于后续请求的身份验证。",
    responses={
        200: {
            "description": "登录成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 0,
                        "msg": SuccessMessages.LOGIN_SUCCESS,
                        "data": {
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "token_type": "bearer"
                        }
                    }
                }
            }
        },
        400: {
            "description": "登录失败",
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.INVALID_CREDENTIALS,
                        "msg": ErrorMessages.INVALID_CREDENTIALS,
                        "data": None
                    }
                }
            }
        },
        401: {
            "description": "认证失败",
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.INVALID_TOKEN,
                        "msg": ErrorMessages.INVALID_TOKEN,
                        "data": None
                    }
                }
            }
        }
    }
)
def login(
    *,
    db: Session = Depends(deps.get_db),
    login_data: LoginRequest,
) -> ResponseModel[Token]:
    """用户登录接口
    
    使用用户名和密码登录，获取访问令牌
    
    Args:
        db: 数据库会话
        login_data: 登录信息（用户名和密码）
        
    Returns:
        ResponseModel[Token]: 标准响应，包含访问令牌信息
    """
    user = UserService.authenticate(db, login_data.username, login_data.password)
    if not user:
        raise APIException(
            code=ErrorCode.INVALID_CREDENTIALS,
            message=ErrorMessages.INVALID_CREDENTIALS
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer"
    }
    return ResponseModel.success(
        data=Token(**token_data),
        msg=SuccessMessages.LOGIN_SUCCESS
    )

@router.post(
    "/register",
    response_model=ResponseModel[UserSchema],
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="创建新用户。用户名必须是3-20个字符，只能包含字母、数字、下划线和连字符。密码必须是6-20个字符。",
    responses={
        201: {
            "description": "注册成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 0,
                        "msg": SuccessMessages.REGISTER_SUCCESS,
                        "data": {
                            "id": 1,
                            "username": "john_doe"
                        }
                    }
                }
            }
        },
        400: {
            "description": "注册失败",
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.USER_EXISTS,
                        "msg": ErrorMessages.USER_EXISTS,
                        "data": None
                    }
                }
            }
        }
    }
)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> ResponseModel[UserSchema]:
    """用户注册接口
    
    创建新用户
    
    Args:
        db: 数据库会话
        user_in: 用户注册信息
        
    Returns:
        ResponseModel[User]: 标准响应，包含创建的用户信息
    """
    if UserService.get_by_username(db, user_in.username):
        raise APIException(
            code=ErrorCode.USER_EXISTS,
            message=ErrorMessages.USER_EXISTS
        )
    
    user = UserService.create(db, user_in)
    return ResponseModel.success(
        data=user,
        msg=SuccessMessages.REGISTER_SUCCESS
    )

@router.post(
    "/test-token",
    response_model=ResponseModel[UserSchema],
    status_code=status.HTTP_200_OK,
    summary="测试令牌",
    description="测试访问令牌是否有效。需要在请求头中携带有效的访问令牌。",
    responses={
        200: {
            "description": "令牌有效",
            "content": {
                "application/json": {
                    "example": {
                        "code": 0,
                        "msg": SuccessMessages.TOKEN_VALID,
                        "data": {
                            "id": 1,
                            "username": "john_doe"
                        }
                    }
                }
            }
        },
        401: {
            "description": "认证失败",
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.INVALID_TOKEN,
                        "msg": ErrorMessages.INVALID_TOKEN,
                        "data": None
                    }
                }
            }
        },
        404: {
            "description": "用户不存在",
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.USER_NOT_FOUND,
                        "msg": ErrorMessages.USER_NOT_FOUND,
                        "data": None
                    }
                }
            }
        }
    }
)
def test_token(current_user: User = Depends(deps.get_current_user)) -> ResponseModel[UserSchema]:
    """令牌测试接口
    
    测试访问令牌是否有效
    
    Args:
        current_user: 当前登录用户（通过依赖注入获取）
        
    Returns:
        ResponseModel[User]: 标准响应，包含当前用户信息
    """
    return ResponseModel.success(
        data=current_user,
        msg=SuccessMessages.TOKEN_VALID
    ) 