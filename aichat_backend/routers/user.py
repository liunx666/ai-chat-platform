"""
用户模块路由层
提供用户注册、登录、获取用户信息等 REST API 接口
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud.user import update_user
from models.user import User
from schemas.user import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from config.db_conf import get_db
from crud import user as user_crud
from utils.response import success_response
from utils.auth import get_current_user


router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register(user_request: UserRequest, db: AsyncSession = Depends(get_db)):
    """
    用户注册接口

    Request Body:
    - username: 用户名
    - password: 密码
    """
    # 检查用户名是否存在
    existing_user = await user_crud.get_by_username(db, username=user_request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    new_user = await user_crud.create_user(db, user_request)

    user_token = await user_crud.create_token(db, new_user.id)
    token = user_token.token

    response_data = UserAuthResponse(
        token=token,
        userInfo=UserInfoResponse.model_validate(new_user)
    )
    return success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    """
    用户登录接口
    
    Request Body:
        username: 用户名（必填）
        password: 密码（必填）
    """
    user = await user_crud.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    user_token = await user_crud.create_token(db, user.id)
    token = user_token.token

    response_data = UserAuthResponse(
        token=token,
        userInfo=UserInfoResponse.model_validate(user)
    )
    return success_response(message="登录成功", data=response_data)


@router.get("/info")
async def get_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息（需要登录认证）
    
    Headers:
        Authorization: Bearer <token>
    """
    response_data = UserInfoResponse.model_validate(current_user)
    return success_response(message="获取成功", data=response_data)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    用户退出登录（使当前token失效）
    
    Headers:
        Authorization: Bearer <token>
    """
    await user_crud.create_token(db, current_user.id)  # 生成新token，使旧token失效
    return success_response(message="退出成功")


@router.put("/password")
async def change_password(
    password_request: UserChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码（需要登录认证）
    
    Headers:
        Authorization: Bearer <token>
    
    Request Body:
        oldPassword: 旧密码
        newPassword: 新密码（至少6位）
    """
    success = await user_crud.update_user_password(
        db,
        current_user,
        password_request.old_password,
        password_request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    return success_response(message="密码修改成功")
