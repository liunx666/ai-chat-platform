"""
定时任务模块
提供后台定时任务功能，如自动清理软删除的对话
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy import delete, select
import logging

from config.db_conf import async_engine
from models.conversation import Conversation, Message

# 配置日志
logger = logging.getLogger(__name__)

# 创建调度器
scheduler = AsyncIOScheduler()


async def cleanup_soft_deleted_conversations():
    """
    定时清理软删除的对话
    
    功能：
    - 删除 is_deleted=1 且更新时间超过30天的对话
    - 级联删除关联的消息记录
    
    执行时间：每天凌晨 2:00 执行
    """
    try:
        logger.info("[定时任务] 开始清理软删除的对话...")
        
        # 计算30天前的时间
        threshold_time = datetime.now() - timedelta(days=30)
        
        async with async_engine.begin() as conn:
            # 1. 先查询符合条件的对话数量
            result = await conn.execute(
                select(Conversation.id).where(
                    Conversation.is_deleted == 1,
                    Conversation.updated_at < threshold_time
                )
            )
            conversation_ids = [row[0] for row in result.fetchall()]
            
            if not conversation_ids:
                logger.info("[定时任务] 没有需要清理的对话")
                return
            
            # 2. 删除关联的消息
            message_result = await conn.execute(
                delete(Message).where(Message.conversation_id.in_(conversation_ids))
            )
            deleted_messages = message_result.rowcount
            
            # 3. 删除对话
            conversation_result = await conn.execute(
                delete(Conversation).where(Conversation.id.in_(conversation_ids))
            )
            deleted_conversations = conversation_result.rowcount
            
            logger.info(
                f"[定时任务] 清理完成：删除 {deleted_conversations} 个对话，"
                f"{deleted_messages} 条消息"
            )
            
    except Exception as e:
        logger.error(f"[定时任务] 清理失败: {e}")


def setup_scheduler():
    """
    配置并启动定时任务调度器
    
    定时任务列表：
    - cleanup_soft_deleted_conversations: 每天凌晨 2:00 执行
    """
    # 添加定时任务：每天凌晨 2:00 清理软删除的对话
    scheduler.add_job(
        cleanup_soft_deleted_conversations,
        CronTrigger(hour=2, minute=0),
        id='cleanup_soft_deleted',
        name='清理软删除对话',
        replace_existing=True
    )
    
    # 启动调度器
    scheduler.start()
    logger.info("[定时任务] 调度器已启动")


def shutdown_scheduler():
    """
    关闭定时任务调度器
    """
    scheduler.shutdown()
    logger.info("[定时任务] 调度器已关闭")
