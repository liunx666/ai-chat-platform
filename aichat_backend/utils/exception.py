"""
全局异常处理模块
为 FastAPI 应用提供统一的异常捕获和 JSON 格式响应
支持开发环境和生产环境的差异化错误信息暴露
"""

import os
import traceback
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

# 开发模式开关：True 返回详细错误信息（含堆栈），False 仅返回简要信息
# 生产环境务必设置为 False，避免敏感信息泄露
# 开发模式开关：根据环境变量动态设置，生产环境务必设置为 False
# 用法：设置环境变量 DEBUG_MODE=true 开启调试模式
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    处理业务逻辑层面主动抛出的 HTTPException
    
    Args:
        request: FastAPI 请求对象（用于日志记录）
        exc: HTTPException 对象（含状态码和错误详情）
        
    Returns:
        JSONResponse: 统一格式的错误响应 {code, message, data}
        
    Note:
        此类异常通常由业务代码主动抛出，如 404 资源不存在、400 参数错误
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    处理数据库完整性约束冲突异常
    
    Args:
        request: FastAPI 请求对象
        exc: IntegrityError 异常对象
        
    Returns:
        JSONResponse: 包含友好错误信息的 JSON 响应
        
    Strategy:
        根据错误信息中的约束关键字，转换为用户可理解的错误提示：
        - 用户名重复 → "用户名已存在"
        - 外键冲突 → "关联数据不存在"
        - 其他约束 → 通用提示
        
    Security:
        DEBUG_MODE 控制是否暴露数据库内部错误信息
    """
    error_msg = str(exc.orig) if exc.orig else str(exc)

    # 根据约束关键字判断具体错误类型
    if "username_UNIQUE" in error_msg or "Duplicate entry" in error_msg:
        detail = "用户名已存在"
    elif "phone_UNIQUE" in error_msg:
        detail = "手机号已存在"
    elif "FOREIGN KEY" in error_msg:
        detail = "关联数据不存在"
    else:
        detail = "数据约束冲突，请检查输入"

    # 开发模式：附加调试信息
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": "IntegrityError",
            "error_detail": error_msg,
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,
            "message": detail,
            "data": error_data
        }
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """
    处理 SQLAlchemy 数据库操作异常（连接超时、语法错误等）
    
    Args:
        request: FastAPI 请求对象
        exc: SQLAlchemyError 异常对象
        
    Returns:
        JSONResponse: 500 状态码 + 错误信息
        
    Security:
        开发模式返回完整堆栈，生产模式仅返回通用错误信息
        避免向外部暴露数据库结构信息
    """
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,
            "error_detail": str(exc),
            "traceback": traceback.format_exc(),
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "数据库操作失败，请稍后重试",
            "data": error_data
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    兜底异常处理器：捕获所有未被特定处理器处理的异常
    
    Args:
        request: FastAPI 请求对象
        exc: 任意未捕获的异常对象
        
    Returns:
        JSONResponse: 500 状态码 + 通用错误信息
        
    Security:
        生产环境不应暴露异常类型和堆栈跟踪
    """
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,
            "error_detail": str(exc),
            "traceback": traceback.format_exc(),
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": error_data
        }
    )



