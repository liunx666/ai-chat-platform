"""
对话模块路由
提供对话和消息相关的 RESTful API 接口
"""

import math
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from models.user import User
from schemas.conversation import (
    ConversationCreateRequest,
    ConversationUpdateRequest,
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse,
    ConversationListData
)
from utils.auth import get_current_user
from utils.response import success_response
from crud import conversation as conversation_crud

router = APIRouter(prefix="/api/conversation", tags=["对话管理"])


def get_default_tenant_id(user: User) -> str:
    """获取用户默认租户ID"""
    return getattr(user, 'tenant_id', 'default')


@router.post("/create", summary="创建新对话")
async def create_conversation(
    request: ConversationCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新对话

    - 创建一个新的对话会话
    - 默认标题为"新对话"，可通过 title 参数指定
    - 返回创建的对话信息
    """
    tenant_id = get_default_tenant_id(user)
    conversation = await conversation_crud.create_conversation(
        db=db,
        user_id=user.id,
        tenant_id=tenant_id,
        title=request.title
    )
    return success_response(
        data=ConversationResponse.model_validate(conversation),
        message="对话创建成功"
    )


@router.get("/list", summary="获取对话列表")
async def get_conversation_list(
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的对话列表（分页）

    - 按更新时间倒序排列
    - 返回对话列表和分页信息
    """
    tenant_id = get_default_tenant_id(user)
    conversations, total = await conversation_crud.get_conversation_list(
        db=db,
        user_id=user.id,
        tenant_id=tenant_id,
        page=page,
        page_size=page_size
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return success_response(
        data=ConversationListData(
            items=[ConversationResponse.model_validate(c) for c in conversations],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        ),
        message="获取成功"
    )


@router.get("/detail/{conversation_id}", summary="获取对话详情")
async def get_conversation_detail(
    conversation_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取对话详情（包含消息列表）

    - 根据对话ID获取对话信息和所有消息
    - 消息按创建时间正序排列
    """
    tenant_id = get_default_tenant_id(user)
    conversation = await conversation_crud.get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
        user_id=user.id,
        tenant_id=tenant_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    messages = await conversation_crud.get_messages_by_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user.id,
        tenant_id=tenant_id
    )

    return success_response(
        data=ConversationDetailResponse(
            conversation=ConversationResponse.model_validate(conversation),
            messages=[MessageResponse.model_validate(m) for m in messages]
        ),
        message="获取成功"
    )


@router.put("/update/{conversation_id}", summary="更新对话")
async def update_conversation(
    conversation_id: int,
    request: ConversationUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新对话（目前只支持修改标题）

    - 根据对话ID更新对话信息
    - 只能更新自己的对话
    """
    tenant_id = get_default_tenant_id(user)
    conversation = await conversation_crud.update_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user.id,
        tenant_id=tenant_id,
        title=request.title
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    return success_response(
        data=ConversationResponse.model_validate(conversation),
        message="更新成功"
    )


@router.delete("/delete/{conversation_id}", summary="删除对话")
async def delete_conversation(
    conversation_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除对话（软删除）

    - 将对话标记为已删除状态
    - 只会更新对话的删除标记，不删除关联的消息
    """
    tenant_id = get_default_tenant_id(user)
    result = await conversation_crud.delete_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user.id,
        tenant_id=tenant_id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    return success_response(message="删除成功")
