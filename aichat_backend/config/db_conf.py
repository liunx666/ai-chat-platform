"""
数据库配置模块
使用 SQLAlchemy 异步引擎连接 MySQL 数据库
提供数据库会话工厂和依赖注入函数
"""

import os
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 从环境变量加载数据库配置（避免密码硬编码）
# 若环境变量未设置，回退到默认值（仅开发环境使用）
# 生产环境务必通过环境变量或密钥管理服务注入真实凭据
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "ai_chat")

ASYNC_DATABASE_URL = (
    f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8"
)

# 创建异步数据库引擎
# pool_size: 连接池常驻连接数（可通过 DB_POOL_SIZE 环境变量调整）
# max_overflow: 超出 pool_size 后额外允许的连接数
# pool_recycle: 连接回收时间（秒），防止 MySQL 8小时断连
# echo: 打印 SQL 语句（通过 DB_ECHO 环境变量控制，生产环境默认关闭）
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600"))
)

# 异步会话工厂：用于创建数据库会话
# expire_on_commit=False: 提交后不使对象过期，避免惰性加载导致的额外查询
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """
    数据库会话生成器（FastAPI 依赖注入使用）
    
    使用 async with 创建会话，请求结束自动提交或回滚。
    
    Yields:
        AsyncSession: SQLAlchemy 异步会话对象
        
    Raises:
        捕获所有异常后执行 rollback 并重新抛出，确保异常可被上层异常处理器捕获
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()