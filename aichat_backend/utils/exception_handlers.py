"""
异常处理器注册模块
统一注册所有全局异常处理器，确保异常处理顺序正确
"""

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils.exception import (
    http_exception_handler,
    integrity_error_handler,
    sqlalchemy_error_handler,
    general_exception_handler
)


def register_exception_handlers(app):
    """
    注册全局异常处理器（注册顺序很重要）
    
    Args:
        app: FastAPI 应用实例
        
    Registration Order:
        1. HTTPException: 业务逻辑异常（最具体）
        2. IntegrityError: 数据库完整性约束异常
        3. SQLAlchemyError: 数据库操作异常
        4. Exception: 兜底异常（最通用）
        
    Principle:
        子类在前，父类在后；具体在前，抽象在后
        确保异常被最匹配的处理器捕获
        
    Usage:
        # 在 main.py 中调用
        register_exception_handlers(app)
    """
    # 业务逻辑异常（如 404、400 等）
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # 数据库完整性约束异常（唯一键冲突、外键约束等）
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    
    # 数据库操作异常（连接超时、SQL语法错误等）
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    
    # 兜底异常处理器（捕获所有未处理的异常）
    app.add_exception_handler(Exception, general_exception_handler)
