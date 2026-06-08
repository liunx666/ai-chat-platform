"""
统一响应格式工具模块
为 API 提供标准化的 JSON 响应格式
"""

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(message: str = 'success', data=None):
    """
    构建统一的成功响应
    
    Args:
        message: 响应消息（默认'success'）
        data:    响应数据（可选，可以是字典、列表、Pydantic模型等）
        
    Returns:
        JSONResponse: 统一格式的 JSON 响应
        
    Response Format:
        {
            "code": 200,
            "message": "操作成功",
            "data": {...}
        }
        
    Usage:
        return success_response(message="登录成功", data=response_data)
        
    Note:
        使用 jsonable_encoder 确保 Pydantic 模型和 ORM 对象可正确序列化
    """
    content = {
        "code": 200,
        "message": message,
        "data": data
    }
    return JSONResponse(content=jsonable_encoder(content))