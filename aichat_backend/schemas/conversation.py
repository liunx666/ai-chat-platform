"""
对话模块 Pydantic Schema
定义对话相关的请求/响应数据模型，用于 API 数据验证和序列化
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MessageContent(BaseModel):
    """消息内容模型"""
    role: str = Field(..., description="消息角色：user=用户, assistant=AI, system=系统")
    content: str = Field(..., description="消息内容")


class ConversationCreateRequest(BaseModel):
    """创建对话请求"""
    title: Optional[str] = Field(None, max_length=255, description="对话标题，默认'新对话'")


class ConversationUpdateRequest(BaseModel):
    """更新对话请求"""
    title: Optional[str] = Field(None, max_length=255, description="对话标题")


class ConversationListRequest(BaseModel):
    """对话列表查询请求"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class ConversationResponse(BaseModel):
    """对话响应模型"""
    id: int = Field(..., description="对话ID")
    tenant_id: str = Field(..., description="租户ID")
    user_id: int = Field(..., description="用户ID")
    title: str = Field(..., description="对话标题")
    is_deleted: int = Field(..., description="软删除标记")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """消息响应模型（合并存储：用户问题和AI回复在同一行）"""
    id: int = Field(..., description="消息ID")
    tenant_id: str = Field(..., description="租户ID")
    user_id: int = Field(..., description="用户ID")
    conversation_id: int = Field(..., description="对话ID")
    role: str = Field(..., description="消息角色")
    content: str = Field(..., description="用户问题内容")
    ai_response: Optional[str] = Field(None, description="AI回复内容")
    thinking_content: Optional[str] = Field(None, description="AI推理过程")
    token_count: int = Field(0, description="消耗token数量")
    model: str = Field(None, description="AI模型")
    created_at: Optional[datetime] = Field(None, description="创建时间（用户提问时间）")
    responded_at: Optional[datetime] = Field(None, description="AI回复时间")

    model_config = {"from_attributes": True}


class ConversationDetailResponse(BaseModel):
    """对话详情响应（包含消息列表）"""
    conversation: ConversationResponse = Field(..., description="对话信息")
    messages: List[MessageResponse] = Field(..., description="消息列表")


class ConversationListData(BaseModel):
    """对话列表数据"""
    items: List[ConversationResponse] = Field(..., description="对话列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
