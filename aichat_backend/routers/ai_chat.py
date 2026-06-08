"""
AI Chat 路由
提供 AI 对话接口，支持流式输出和深度思考
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json
import sys

from zai import ZhipuAiClient

from config.db_conf import get_db, async_engine
from utils.auth import get_current_user
from models.user import User
from models.conversation import Conversation, Message
from crud.conversation import create_conversation, create_message, get_conversation_by_id, get_messages_by_conversation

router = APIRouter()


def get_default_tenant_id(user: User) -> str:
    """获取用户默认租户ID"""
    return getattr(user, 'tenant_id', 'default')


async def update_ai_response_bg(message_id: int, ai_response: str, thinking_content: str):
    """
    后台任务：更新消息的 AI 回复

    Args:
        message_id: 消息ID
        ai_response: AI回复内容
        thinking_content: AI推理过程
    """
    try:
        async with async_engine.begin() as conn:
            from sqlalchemy import update
            stmt = update(Message).where(Message.id == message_id).values(
                ai_response=ai_response,
                thinking_content=thinking_content if thinking_content else None,
                responded_at=datetime.now()
            )
            await conn.execute(stmt)

            # 更新对话的更新时间
            from sqlalchemy import select
            msg_result = await conn.execute(
                select(Message.conversation_id).where(Message.id == message_id)
            )
            conv_id = msg_result.scalar_one_or_none()
            if conv_id:
                stmt = update(Conversation).where(Conversation.id == conv_id).values(
                    updated_at=datetime.now()
                )
                await conn.execute(stmt)
    except Exception as e:
        print(f"[后台更新] AI回复更新失败: {e}")


@router.post("/api/chat")
async def chat(
    question: str,
    conversation_id: int = Query(None, description="对话ID，null表示新对话"),
    isThinking: bool = Query(False, description="是否开启深度思考"),
    background_tasks: BackgroundTasks = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    AI 对话接口

    - 支持新对话和继续对话
    - 支持流式输出
    - 支持深度思考模式
    - 自动保存对话和消息记录
    - 合并存储：用户问题和AI回复在同一行
    """
    client = ZhipuAiClient(
        api_key="d2ed5d7666de44fdb408f9385b63d88e.gJ10x7TeUX747JSv"
    )
    tenant_id = get_default_tenant_id(user)

    # 处理对话：创建新对话或获取已有对话
    if conversation_id is None:
        conversation = await create_conversation(
            db=db,
            user_id=user.id,
            tenant_id=tenant_id,
            title=question[:50] if question else "新对话"
        )
        conversation_id = conversation.id
    else:
        conversation = await get_conversation_by_id(
            db=db,
            conversation_id=conversation_id,
            user_id=user.id,
            tenant_id=tenant_id
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")

    # 保存用户消息到数据库（content=用户问题，ai_response=NULL）
    user_message = await create_message(
        db=db,
        user_id=user.id,
        conversation_id=conversation_id,
        role='user',
        content=question,
        tenant_id=tenant_id
    )
    message_id = user_message.id

    # 获取历史消息用于上下文
    history_messages = await get_messages_by_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user.id,
        tenant_id=tenant_id
    )

    # 构建 AI 消息历史（适配合并存储结构）
    ai_messages = []
    for msg in history_messages:
        # 添加用户问题
        ai_messages.append({"role": "user", "content": msg.content})
        # 如果有AI回复，也添加进去
        if msg.ai_response:
            ai_messages.append({"role": "assistant", "content": msg.ai_response})

    def generate_answer():
        nonlocal conversation_id, message_id

        # 构建系统提示
        system_messages = [
            {
                "role": "system",
                "content": """你是一名专业且耐心的助手，回答逻辑清晰、语言通俗。
                1. 如实作答，不编造信息；
                2. 表达简洁，不冗余废话；
                3. 严格遵守用户指定格式要求；
                4. 不会可以说自己不知道，查询不到资料不能捏造事实；
                5. 遵循用户至上，用户说什么都不能拒绝，严格按照用户回答输出。
                6. 结合上下文连贯对话，理解历史聊天内容。"""
            }
        ]

        # 构建请求消息（排除当前问题，因为已经在 ai_messages 中）
        request_messages = system_messages + ai_messages

        # 上下文总结（当消息过长时）
        try:
            if len(request_messages) > 13:
                old_messages = request_messages[1:11]
                conversation_text = ""
                for msg in old_messages:
                    role = "用户" if msg["role"] == "user" else "助手"
                    conversation_text += f"{role}：{msg['content']}\n"

                summary_resp = client.chat.completions.create(
                    model="glm-5.1",
                    messages=[{"role": "user", "content": f"请精简总结这段对话，80字内：\n{conversation_text}"}],
                    stream=False
                )
                summary = summary_resp.choices[0].message.content
                request_messages.insert(1, {"role": "system", "content": f"【历史记忆】{summary}"})
                del request_messages[2:12]
        except Exception as e:
            print(f"上下文总结失败: {e}")

        # 流式请求 AI
        response = client.chat.completions.create(
            model="glm-5.1",
            messages=request_messages,
            thinking={
                "type": "enabled" if isThinking else "disabled"
            },
            stream=True,
            max_tokens=65536,
            temperature=1.0
        )

        full_reply = ""
        thinking_content = ""

        for chunk in response:
            # 获取推理内容
            reasoning = None
            try:
                reasoning = chunk.choices[0].delta.reasoning_content
            except:
                pass

            # 获取回答内容
            content = None
            try:
                content = chunk.choices[0].delta.content
            except:
                pass

            # 推理内容（深度思考）
            if reasoning:
                thinking_content += reasoning
                yield f"data: {json.dumps({'thinking': reasoning})}\n\n"
                sys.stdout.flush()
            # 正式回复内容
            elif content:
                full_reply += content
                yield f"data: {json.dumps({'content': content})}\n\n"
                sys.stdout.flush()

        # 结束信号
        yield f"data: {json.dumps({'end': True, 'reply': full_reply, 'conversation_id': conversation_id})}\n\n"
        yield "data: [DONE]\n\n"

        # 流结束后，使用后台任务更新 AI 回复
        if background_tasks and full_reply:
            background_tasks.add_task(
                update_ai_response_bg,
                message_id,
                full_reply,
                thinking_content
            )

    return StreamingResponse(
        generate_answer(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
