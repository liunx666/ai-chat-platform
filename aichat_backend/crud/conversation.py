"""
对话模块数据访问层（CRUD操作）
提供对话和消息的创建、查询、更新、删除等数据库操作
"""

from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.conversation import Conversation, Message
from schemas.conversation import ConversationCreateRequest, ConversationUpdateRequest


# =============================================
# 对话（Conversation）CRUD 操作
# =============================================

async def create_conversation(
    db: AsyncSession,
    user_id: int,
    tenant_id: str = 'default',
    title: Optional[str] = None
) -> Conversation:
    """
    创建新对话

    Args:
        db: 数据库会话
        user_id: 用户ID
        tenant_id: 租户ID
        title: 对话标题

    Returns:
        Conversation: 创建的对话对象
    """
    conversation = Conversation(
        tenant_id=tenant_id,
        user_id=user_id,
        title=title or '新对话',
        is_deleted=0,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def get_conversation_by_id(
    db: AsyncSession,
    conversation_id: int,
    user_id: int,
    tenant_id: str = 'default'
) -> Optional[Conversation]:
    """
    根据ID获取对话

    Args:
        db: 数据库会话
        conversation_id: 对话ID
        user_id: 用户ID
        tenant_id: 租户ID

    Returns:
        Optional[Conversation]: 对话对象或None
    """
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.tenant_id == tenant_id,
            Conversation.is_deleted == 0
        )
    )
    return result.scalar_one_or_none()


async def get_conversation_list(
    db: AsyncSession,
    user_id: int,
    tenant_id: str = 'default',
    page: int = 1,
    page_size: int = 20
) -> Tuple[List[Conversation], int]:
    """
    获取用户的对话列表（分页）

    Args:
        db: 数据库会话
        user_id: 用户ID
        tenant_id: 租户ID
        page: 页码
        page_size: 每页数量

    Returns:
        Tuple[List[Conversation], int]: (对话列表, 总数)
    """
    query = select(Conversation).where(
        Conversation.user_id == user_id,
        Conversation.tenant_id == tenant_id,
        Conversation.is_deleted == 0
    ).order_by(desc(Conversation.updated_at))

    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(
        query.offset(offset).limit(page_size)
    )
    conversations = result.scalars().all()

    return list(conversations), total


async def update_conversation(
    db: AsyncSession,
    conversation_id: int,
    user_id: int,
    tenant_id: str = 'default',
    title: Optional[str] = None
) -> Optional[Conversation]:
    """
    更新对话标题

    Args:
        db: 数据库会话
        conversation_id: 对话ID
        user_id: 用户ID
        tenant_id: 租户ID
        title: 新标题

    Returns:
        Optional[Conversation]: 更新后的对话对象或None
    """
    conversation = await get_conversation_by_id(db, conversation_id, user_id, tenant_id)
    if not conversation:
        return None

    if title is not None:
        conversation.title = title
    conversation.updated_at = datetime.now()

    await db.commit()
    await db.refresh(conversation)
    return conversation


async def delete_conversation(
    db: AsyncSession,
    conversation_id: int,
    user_id: int,
    tenant_id: str = 'default'
) -> bool:
    """
    软删除对话

    Args:
        db: 数据库会话
        conversation_id: 对话ID
        user_id: 用户ID
        tenant_id: 租户ID

    Returns:
        bool: 是否删除成功
    """
    conversation = await get_conversation_by_id(db, conversation_id, user_id, tenant_id)
    if not conversation:
        return False

    conversation.is_deleted = 1
    conversation.updated_at = datetime.now()
    await db.commit()
    return True


# =============================================
# 消息（Message）CRUD 操作
# =============================================

async def create_message(
    db: AsyncSession,
    user_id: int,
    conversation_id: int,
    role: str,
    content: str,
    tenant_id: str = 'default',
    thinking_content: Optional[str] = None,
    token_count: int = 0,
    model: str = 'glm-5.1'
) -> Message:
    """
    创建新消息（合并存储：用户问题和AI回复在同一行）

    Args:
        db: 数据库会话
        user_id: 用户ID
        conversation_id: 对话ID
        role: 消息角色
        content: 用户问题内容
        tenant_id: 租户ID
        thinking_content: AI推理过程
        token_count: token消耗
        model: AI模型

    Returns:
        Message: 创建的消息对象
    """
    message = Message(
        tenant_id=tenant_id,
        user_id=user_id,
        conversation_id=conversation_id,
        role=role,
        content=content,
        thinking_content=thinking_content,
        token_count=token_count,
        model=model,
        created_at=datetime.now()
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    # 更新对话的更新时间
    await db.execute(
        update(Conversation).where(
            Conversation.id == conversation_id
        ).values(updated_at=datetime.now())
    )
    await db.commit()

    return message


async def get_messages_by_conversation(
    db: AsyncSession,
    conversation_id: int,
    user_id: int,
    tenant_id: str = 'default'
) -> List[Message]:
    """
    获取对话的所有消息（按时间顺序）

    Args:
        db: 数据库会话
        conversation_id: 对话ID
        user_id: 用户ID
        tenant_id: 租户ID

    Returns:
        List[Message]: 消息列表
    """
    # 先验证对话归属
    conversation = await get_conversation_by_id(db, conversation_id, user_id, tenant_id)
    if not conversation:
        return []

    result = await db.execute(
        select(Message).where(
            Message.conversation_id == conversation_id,
            Message.tenant_id == tenant_id
        ).order_by(Message.created_at)
    )
    return list(result.scalars().all())


async def get_message_by_id(
    db: AsyncSession,
    message_id: int,
    user_id: int,
    tenant_id: str = 'default'
) -> Optional[Message]:
    """
    根据ID获取消息

    Args:
        db: 数据库会话
        message_id: 消息ID
        user_id: 用户ID
        tenant_id: 租户ID

    Returns:
        Optional[Message]: 消息对象或None
    """
    result = await db.execute(
        select(Message).where(
            Message.id == message_id,
            Message.user_id == user_id,
            Message.tenant_id == tenant_id
        )
    )
    return result.scalar_one_or_none()


async def delete_messages_by_conversation(
    db: AsyncSession,
    conversation_id: int,
    user_id: int,
    tenant_id: str = 'default'
) -> bool:
    """
    删除对话的所有消息

    Args:
        db: 数据库会话
        conversation_id: 对话ID
        user_id: 用户ID
        tenant_id: 租户ID

    Returns:
        bool: 是否删除成功
    """
    conversation = await get_conversation_by_id(db, conversation_id, user_id, tenant_id)
    if not conversation:
        return False

    await db.execute(
        update(Message).where(
            Message.conversation_id == conversation_id,
            Message.tenant_id == tenant_id
        )
    )
    await db.commit()
    return True
