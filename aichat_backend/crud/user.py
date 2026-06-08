"""
用户模块数据访问层（CRUD操作）
提供用户注册、登录、认证、令牌管理等数据库操作
"""

import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select,update
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User, UserToken
from schemas.user import UserRequest, UserUpdateRequest
from utils import security
from utils.security import verify_password


# 根据用户名查询用户
async def get_by_username(db: AsyncSession, username: str):
    """
    根据用户名查询用户
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    """
    创建用户

    默认角色为 'user'（普通用户）
    默认租户为 'default'
    """
    # 检查用户名是否已存在
    existing_user = await get_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 手动获取下一个ID（因为数据库表没有设置AUTO_INCREMENT）
    result = await db.execute(select(User.id).order_by(User.id.desc()).limit(1))
    max_id = result.scalar_one_or_none()
    next_id = max_id + 1 if max_id else 1

    hashed_password = security.get_hash_password(user_data.password)

    user = User(
        id=next_id,
        username=user_data.username,
        password=hashed_password,
        tenant_id='default',
        role='user',
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# 创建token
async def create_token(db: AsyncSession, user_id: int):
    """
    创建token
    """

    token = str(uuid.uuid4())

    expires_at = datetime.now() + timedelta(days=7)

    stmt = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(stmt)
    user_token = result.scalar_one_or_none()

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        db.add(user_token)

    await db.commit()
    return user_token


# 用户认证（用户名+密码）
async def authenticate_user(db: AsyncSession, username: str, password: str):
    """
    用户认证：验证用户名和密码
    """
    user = await get_by_username(db, username)
    if not user:
        return None
    
    if not verify_password(password, user.password):
        return None
    
    return user


# 根据 token 查询用户
async def get_user_by_token(db: AsyncSession, token: str):
    """
    根据令牌查询用户（令牌认证）
    
    Args:
        db: 数据库会话
        token: 认证令牌
        
    Returns:
        User or None: 令牌对应的用户对象，令牌无效或过期返回None
        
    Steps:
        1. 查询令牌记录
        2. 验证令牌是否存在且未过期
        3. 根据 user_id 查询用户信息
    """
    # 查询令牌
    stmt = select(UserToken).where(UserToken.token == token)
    result = await db.execute(stmt)
    user_token = result.scalar_one_or_none()

    # 验证令牌有效性和过期时间
    if not user_token or user_token.expires_at < datetime.now():
        return None

    # 查询用户信息
    user_stmt = select(User).where(User.id == user_token.user_id)
    user_result = await db.execute(user_stmt)
    return user_result.scalar_one_or_none()


# 更新用户信息 update更新
async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    """
    更新用户信息

    Args:
        db: 数据库会话
        username: 用户名
        user_data: 更新数据

    Returns:
        User or None: 更新成功的用户对象，失败返回None

    Steps:
        1. 根据用户名查询用户
        2. 验证用户是否存在
        3. 更新用户信息
        4. 提交数据库事务
    """
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_none= True,
        exclude_unset=True
    ))
    result = await db.execute(query)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")

    updateuser = await get_user_by_username(db, username)
    return updateuser

# 修改密码 => 验证旧密码 => 新密码加密 => 更新密码
async def update_user_password(db: AsyncSession,
                               user:User,
                               old_password: str,
                               new_password: str
                               ):
    """
    修改用户密码

    Args:
        db: 数据库会话
        user: 用户对象
        old_password: 旧密码
        new_password: 新密码

    Returns:
        User or None: 修改成功的用户对象，失败返回None

    Steps:
        1. 验证旧密码
        2. 新密码加密
        3. 更新用户密码
        4. 提交数据库事务
    """

    if not security.verify_password(old_password, user.password):
        return False

    new_password = security.get_hash_password(new_password)

    user.password = new_password
    # SQLAlchemy 提交数据库事务 真正接管这个User对象 ,确保可以commit
    # 规避 session 过期或者关闭不能提交
    db.add(user)

    await db.commit()
    await db.refresh(user)
    return True