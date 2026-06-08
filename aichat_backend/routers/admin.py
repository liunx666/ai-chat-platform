"""
管理员路由
提供管理员专用接口，包括用户管理、对话管理等

注意：管理员账户需要直接在数据库中手动创建，更安全
SQL: UPDATE user SET role = 'admin' WHERE username = '管理员用户名';
"""

import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, delete
from starlette import status

from config.db_conf import get_db
from models.user import User
from models.conversation import Conversation, Message
from utils.auth import get_current_admin
from utils.response import success_response

router = APIRouter(prefix="/api/admin", tags=["管理员接口"])


@router.get("/users", summary="获取所有用户列表")
async def get_all_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有用户列表（管理员专用）

    - 支持分页
    - 返回用户基本信息、角色、对话数量
    """
    # 查询总数
    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar() or 0

    # 分页查询用户
    offset = (page - 1) * page_size
    result = await db.execute(
        select(User).order_by(desc(User.created_at)).offset(offset).limit(page_size)
    )
    users = result.scalars().all()

    # 统计每个用户的对话数量
    user_list = []
    for u in users:
        conv_count = await db.execute(
            select(func.count()).select_from(Conversation).where(Conversation.user_id == u.id)
        )
        conv_total = conv_count.scalar() or 0

        user_list.append({
            "id": u.id,
            "username": u.username,
            "tenant_id": u.tenant_id,
            "role": u.role,
            "conversation_count": conv_total,
            "created_at": u.created_at.isoformat() if u.created_at else None
        })

    return success_response(
        data={
            "items": user_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 0
        },
        message="获取成功"
    )


@router.get("/users/{user_id}", summary="获取单个用户详情")
async def get_user_detail(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个用户详情（管理员专用）

    - 用户基本信息
    - 对话统计（总数、已删除数）
    - 消息统计
    """
    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 统计对话数量
    conv_count = await db.execute(
        select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)
    )
    total_conversations = conv_count.scalar() or 0

    # 统计已删除对话数量
    deleted_count = await db.execute(
        select(func.count()).select_from(Conversation).where(
            Conversation.user_id == user_id,
            Conversation.is_deleted == 1
        )
    )
    deleted_conversations = deleted_count.scalar() or 0

    # 统计消息数量
    msg_count = await db.execute(
        select(func.count()).select_from(Message).where(Message.user_id == user_id)
    )
    total_messages = msg_count.scalar() or 0

    # 统计Token消耗
    token_sum = await db.execute(
        select(func.sum(Message.token_count)).where(Message.user_id == user_id)
    )
    total_tokens = token_sum.scalar() or 0

    return success_response(
        data={
            "id": user.id,
            "username": user.username,
            "tenant_id": user.tenant_id,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "statistics": {
                "total_conversations": total_conversations,
                "active_conversations": total_conversations - deleted_conversations,
                "deleted_conversations": deleted_conversations,
                "total_messages": total_messages,
                "total_tokens": total_tokens
            }
        },
        message="获取成功"
    )


@router.put("/users/{user_id}/role", summary="修改用户角色")
async def update_user_role(
    user_id: int,
    role: str = Query(..., description="角色：admin 或 user"),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    修改用户角色（管理员专用）

    - 可以将用户设置为管理员或普通用户
    - 不能修改自己的角色
    """
    if role not in ['admin', 'user']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色必须是 admin 或 user"
        )

    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 不能修改自己的角色
    if target_user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的角色"
        )

    # 更新角色
    target_user.role = role
    await db.commit()

    return success_response(
        data={
            "id": target_user.id,
            "username": target_user.username,
            "role": target_user.role
        },
        message="角色更新成功"
    )


@router.get("/conversations", summary="获取所有对话列表")
async def get_all_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Query(None, description="筛选指定用户的对话"),
    include_deleted: bool = Query(True, description="是否包含软删除的对话"),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有对话列表（管理员专用）

    - 支持分页
    - 可按用户ID筛选
    - 可选择是否包含软删除的对话（默认包含）
    - 显示对话基本信息和消息数量
    """
    # 构建查询
    query = select(Conversation)

    if user_id:
        query = query.where(Conversation.user_id == user_id)

    if not include_deleted:
        query = query.where(Conversation.is_deleted == 0)

    # 查询总数
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # 分页查询
    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(desc(Conversation.updated_at)).offset(offset).limit(page_size)
    )
    conversations = result.scalars().all()

    # 统计每个对话的消息数量
    conv_list = []
    for c in conversations:
        msg_count = await db.execute(
            select(func.count()).select_from(Message).where(Message.conversation_id == c.id)
        )
        msg_total = msg_count.scalar() or 0

        # 查询用户名
        user_result = await db.execute(select(User.username).where(User.id == c.user_id))
        username = user_result.scalar_one_or_none() or "未知用户"

        conv_list.append({
            "id": c.id,
            "tenant_id": c.tenant_id,
            "user_id": c.user_id,
            "username": username,
            "title": c.title,
            "is_deleted": c.is_deleted,
            "message_count": msg_total,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None
        })

    return success_response(
        data={
            "items": conv_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 0
        },
        message="获取成功"
    )


@router.get("/conversations/{conversation_id}", summary="获取对话详情和所有消息")
async def get_conversation_detail(
    conversation_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取对话详情和所有消息（管理员专用）

    - 管理员可以查看任何对话的消息
    - 每条消息包含用户问题和AI回复
    - 包含软删除的对话
    """
    # 查询对话
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    # 查询用户名
    user_result = await db.execute(select(User).where(User.id == conversation.user_id))
    user = user_result.scalar_one_or_none()

    # 查询消息（按时间排序）
    result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    )
    messages = result.scalars().all()

    # 统计Token消耗
    token_sum = sum(m.token_count or 0 for m in messages)

    # 统计AI回复数量
    ai_response_count = len([m for m in messages if m.ai_response])

    return success_response(
        data={
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "user_id": conversation.user_id,
                "username": user.username if user else "未知用户",
                "is_deleted": conversation.is_deleted,
                "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
                "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None
            },
            "messages": [
                {
                    "id": m.id,
                    "user_question": m.content,
                    "ai_response": m.ai_response,
                    "thinking_content": m.thinking_content,
                    "token_count": m.token_count,
                    "model": m.model,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                    "responded_at": m.responded_at.isoformat() if m.responded_at else None
                }
                for m in messages
            ],
            "statistics": {
                "total_messages": len(messages),
                "ai_responses": ai_response_count,
                "total_tokens": token_sum
            }
        },
        message="获取成功"
    )


@router.delete("/conversations/{conversation_id}", summary="强制删除对话")
async def force_delete_conversation(
    conversation_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    强制删除对话（管理员专用）

    - 物理删除对话和关联消息
    - 不受软删除限制
    - 删除后无法恢复
    """
    # 查询对话
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    # 统计要删除的消息数量
    msg_count = await db.execute(
        select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id)
    )
    deleted_messages = msg_count.scalar() or 0

    # 删除消息
    await db.execute(
        delete(Message).where(Message.conversation_id == conversation_id)
    )

    # 删除对话
    await db.execute(
        delete(Conversation).where(Conversation.id == conversation_id)
    )

    await db.commit()

    return success_response(
        data={
            "deleted_conversation_id": conversation_id,
            "deleted_messages": deleted_messages
        },
        message="删除成功"
    )


@router.post("/conversations/{conversation_id}/restore", summary="恢复软删除的对话")
async def restore_conversation(
    conversation_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    恢复软删除的对话（管理员专用）

    - 将 is_deleted 设置为 0
    - 用户可以重新看到该对话
    """
    # 查询对话
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    if conversation.is_deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该对话未被删除，无需恢复"
        )

    # 恢复对话
    conversation.is_deleted = 0
    await db.commit()

    return success_response(
        data={
            "id": conversation.id,
            "title": conversation.title,
            "is_deleted": 0
        },
        message="恢复成功"
    )


@router.get("/statistics", summary="获取系统统计信息")
async def get_statistics(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取系统统计信息（管理员专用）

    - 用户统计
    - 对话统计（包括软删除）
    - 消息统计
    - Token消耗统计
    """
    # 用户统计
    user_count = await db.execute(select(func.count()).select_from(User))
    total_users = user_count.scalar() or 0

    admin_count = await db.execute(
        select(func.count()).select_from(User).where(User.role == 'admin')
    )
    total_admins = admin_count.scalar() or 0

    # 对话统计
    conv_count = await db.execute(select(func.count()).select_from(Conversation))
    total_conversations = conv_count.scalar() or 0

    deleted_conv_count = await db.execute(
        select(func.count()).select_from(Conversation).where(Conversation.is_deleted == 1)
    )
    deleted_conversations = deleted_conv_count.scalar() or 0

    # 消息统计（合并存储）
    msg_count = await db.execute(select(func.count()).select_from(Message))
    total_messages = msg_count.scalar() or 0

    # AI回复统计（有 ai_response 的消息数）
    ai_response_count = await db.execute(
        select(func.count()).select_from(Message).where(Message.ai_response.isnot(None))
    )
    ai_responses = ai_response_count.scalar() or 0

    # Token消耗统计
    token_sum = await db.execute(select(func.sum(Message.token_count)))
    total_tokens = token_sum.scalar() or 0

    return success_response(
        data={
            "users": {
                "total": total_users,
                "admins": total_admins,
                "normal_users": total_users - total_admins
            },
            "conversations": {
                "total": total_conversations,
                "active": total_conversations - deleted_conversations,
                "deleted": deleted_conversations
            },
            "messages": {
                "total": total_messages,
                "ai_responses": ai_responses,
                "pending": total_messages - ai_responses
            },
            "tokens": {
                "total": total_tokens
            }
        },
        message="获取成功"
    )
