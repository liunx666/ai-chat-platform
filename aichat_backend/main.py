"""
AI Chat后端主入口文件
基于 FastAPI 框架构建的 RESTful API 服务
主要功能：用户注册登录、AI Chat等接口
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from routers import user, ai_chat, conversation, admin

from utils.exception_handlers import register_exception_handlers
from scheduler import setup_scheduler, shutdown_scheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    启动时：
    - 启动定时任务调度器
    
    关闭时：
    - 关闭定时任务调度器
    """
    # 启动定时任务
    logger.info("应用启动中...")
    setup_scheduler()
    logger.info("定时任务调度器已启动")
    
    yield
    
    # 关闭定时任务
    logger.info("应用关闭中...")
    shutdown_scheduler()
    logger.info("定时任务调度器已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title="AI Chat后端 API",
    description="提供AI Chat的后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 注册全局异常处理器
register_exception_handlers(app)

# CORS 配置：根据环境变量动态配置允许的跨域来源
# 开发环境默认：http://localhost:5173
# 生产环境：通过 ALLOWED_ORIGINS 环境变量配置（逗号分隔）
ALLOWED_ORIGINS = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    根路径健康检查接口
    """
    return {"message": "接口服务已经打开"}


# 注册业务路由模块
app.include_router(user.router)  # 用户相关路由

app.include_router(ai_chat.router)  # ai路由

app.include_router(conversation.router)  # 对话管理路由

app.include_router(admin.router)  # 管理员路由
