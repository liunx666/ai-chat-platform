"""
用户模块数据验证模型（Pydantic Schemas）
定义 API 请求和响应的数据结构
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# --------------------------
# 1. 先定义【基础类】
# --------------------------
class UserInfoBase(BaseModel):
    """
    用户信息基础模型
    """
    id: int
    username: str
    tenant_id: Optional[str] = 'default'
    role: Optional[str] = 'user'

    model_config = ConfigDict(from_attributes=True)

# --------------------------
# 2. 请求类
# --------------------------
class UserRequest(BaseModel):
    """用户注册/登录请求模型"""
    username: str
    password: str

class UserUpdateRequest(BaseModel):
    """用户信息更新请求（补上这个！）"""
    password: Optional[str] = None
    role: Optional[str] = None

class UserChangePasswordRequest(BaseModel):
    """更新用户密码"""
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, alias="newPassword", description="新密码")

# --------------------------
# 3. 响应类
# --------------------------
class UserInfoResponse(UserInfoBase):
    """用户信息响应模型"""
    pass

class UserAuthResponse(BaseModel):
    """用户认证响应模型（登录/注册返回）"""
    token: str
    user_info: UserInfoBase = Field(..., alias="userInfo")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )