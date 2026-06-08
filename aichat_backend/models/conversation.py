"""
对话模块数据模型
定义对话信息和对话消息的 ORM 映射
"""

from datetime import datetime
from sqlalchemy import Index, Integer, String, Enum, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """基础模型类"""
    pass


class Conversation(Base):
    """
    AI 对话信息实体模型
    对应数据库表：ai_conversations

    字段说明：
    - id: 对话ID，主键自增
    - tenant_id: 租户ID，用于多租户数据隔离
    - user_id: 用户ID，关联 user.id
    - title: 对话标题/名字
    - is_deleted: 软删除标记，0=未删除，1=已删除
    - created_at: 创建时间
    - updated_at: 最后更新时间
    """
    __tablename__ = 'ai_conversations'

    __table_args__ = (
        Index('idx_tenant_user', 'tenant_id', 'user_id'),
        Index('idx_user_updated', 'user_id', 'updated_at'),
        Index('idx_tenant_deleted', 'tenant_id', 'is_deleted'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="对话ID")
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, default='default', comment="租户ID")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID")
    title: Mapped[str] = mapped_column(String(255), nullable=True, default='新对话', comment="对话标题")
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="软删除标记")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")

    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class Message(Base):
    """
    AI 对话消息实体模型
    对应数据库表：ai_messages

    字段说明：
    - id: 消息ID，主键自增
    - tenant_id: 租户ID，用于多租户数据隔离
    - user_id: 用户ID，关联 user.id
    - conversation_id: 对话ID，关联 ai_conversations.id
    - role: 消息角色，user=用户, assistant=AI, system=系统
    - content: 用户问题内容
    - ai_response: AI回复内容（合并存储）
    - thinking_content: AI推理过程（深度思考内容）
    - token_count: 消耗token数量
    - model: 使用的AI模型
    - created_at: 创建时间
    - responded_at: AI回复时间
    """
    __tablename__ = 'ai_messages'

    __table_args__ = (
        Index('idx_conversation', 'conversation_id'),
        Index('idx_tenant_user', 'tenant_id', 'user_id'),
        Index('idx_conversation_created', 'conversation_id', 'created_at'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="消息ID")
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, default='default', comment="租户ID")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID")
    conversation_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="对话ID")
    role: Mapped[str] = mapped_column(Enum('user', 'assistant', 'system'), nullable=False, default='user', comment="消息角色")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="用户问题内容")
    ai_response: Mapped[str] = mapped_column(Text, nullable=True, comment="AI回复内容")
    thinking_content: Mapped[str] = mapped_column(Text, nullable=True, comment="AI推理过程")
    token_count: Mapped[int] = mapped_column(Integer, nullable=True, default=0, comment="消耗token数量")
    model: Mapped[str] = mapped_column(String(64), nullable=True, default='glm-5.1', comment="AI模型")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now, comment="创建时间")
    responded_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="AI回复时间")

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id})>"
