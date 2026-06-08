"""
认证工具模块
提供基于令牌的用户认证中间件和权限验证
"""

from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.db_conf import get_db
from crud import user
from models.user import User


async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    认证中间件：验证 Bearer 令牌并获取当前用户

    Args:
        authorization: HTTP Authorization 头部（格式：Bearer <token>）
        db: 数据库会话依赖注入

    Returns:
        User: 认证成功的用户对象

    Raises:
        401 Unauthorized: 令牌无效或已过期

    Usage:
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            # 只有认证用户才能访问
            return {"user": user.username}
    """
    # 提取 Bearer 令牌
    token = authorization.replace("Bearer ", "").strip()

    # 验证令牌有效性并获取用户
    current_user = await user.get_user_by_token(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌或者令牌已过期"
        )

    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    管理员权限验证中间件

    Args:
        current_user: 当前用户（通过 get_current_user 获取）

    Returns:
        User: 管理员用户对象

    Raises:
        403 Forbidden: 非管理员用户

    Usage:
        @router.get("/admin/only")
        async def admin_route(admin: User = Depends(get_current_admin)):
            # 只有管理员才能访问
            return {"admin": admin.username}
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )

    return current_user


def require_role(required_role: str):
    """
    角色权限验证装饰器工厂

    Args:
        required_role: 需要的角色（'admin' 或 'user'）

    Returns:
        依赖注入函数

    Usage:
        @router.get("/admin/data")
        async def admin_data(user: User = Depends(require_role('admin'))):
            return {"data": "admin only"}
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role != required_role and required_role == 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要 {required_role} 角色"
            )
        return current_user

    return role_checker