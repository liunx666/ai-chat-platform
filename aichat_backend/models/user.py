"""
用户模块数据模型
定义用户和用户令牌的 ORM 映射
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Index, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    基础模型类（用户模块独立定义）
    注意：与 news.py 中的 Base 类重复，建议统一到公共模块
    """
    pass


class User(Base):
    """
    用户实体模型
    对应数据库表：user

    字段说明：
    - id: 用户ID，主键自增
    - username: 用户名
    - password: 密码（bcrypt加密存储）
    - tenant_id: 租户ID，用于多租户隔离
    - role: 用户角色（admin=管理员，user=普通用户）
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户 ID")
    username: Mapped[str] = mapped_column(String(255), nullable=True, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=True, comment="密码（bcrypt 加密存储）")
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=True, default='default', comment="租户ID")
    role: Mapped[str] = mapped_column(Enum('admin', 'user'), nullable=True, default='user', comment="用户角色")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="更新时间")

    def __repr__(self):
        """对象字符串表示，用于调试和日志"""
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

    @property
    def is_admin(self) -> bool:
        """判断是否为管理员"""
        return self.role == 'admin'


class UserToken(Base):
    """
    用户令牌模型（用于用户认证）
    对应数据库表：user_token
    
    字段说明：
    - id: 令牌ID，主键自增
    - user_id: 用户ID，外键关联 user.id，不能为空
    - token: 令牌值（UUID格式），唯一约束，不能为空
    - expires_at: 过期时间，不能为空
    - created_at: 创建时间，默认当前时间
    
    索引说明：
    - token_UNIQUE: 令牌唯一索引，加速令牌查询
    - fk_user_token_user_idx: 用户ID索引，加速关联查询
    """
    __tablename__ = 'user_token'

    # 表级约束：创建索引
    __table_args__ = (
        Index('token_UNIQUE', 'token'),
        Index('fk_user_token_user_idx', 'user_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="令牌ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False, comment="用户ID")
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="令牌值")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), comment="创建时间")

    def __repr__(self):
        """对象字符串表示，用于调试和日志"""
        return f"<UserToken(id={self.id}, user_id={self.user_id}, token='{self.token}')>"