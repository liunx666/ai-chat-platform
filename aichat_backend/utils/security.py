"""
密码安全工具模块
提供密码哈希加密和验证功能，基于 bcrypt 算法
"""

import bcrypt


def get_hash_password(password: str):
    """
    密码哈希加密
    
    Args:
        password: 明文密码
        
    Returns:
        str: bcrypt 哈希后的密码字符串
        
    Security:
        1. 自动生成随机盐（salt），相同密码每次哈希结果不同
        2. 使用 bcrypt 算法，计算成本可配置（默认 12 轮）
        3. 返回格式包含算法标识、成本因子、盐和哈希值
        
    Example:
        >>> hash = get_hash_password("mysecret")
        >>> print(hash)  # $2b$12$... (bcrypt 格式)
    """
    # 将密码转换为字节
    password_bytes = password.encode('utf-8')
    
    # 生成盐并哈希密码（bcrypt 默认 rounds=12）
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    
    # 返回字符串格式
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str):
    """
    密码验证：比较明文密码和哈希密码是否匹配
    
    Args:
        plain_password:  用户输入的明文密码
        hashed_password: 数据库中存储的哈希密码
        
    Returns:
        bool: 密码匹配返回 True，否则 False
        
    Security:
        1. 使用恒定时间比较，防止时序攻击
        2. 自动从哈希值中提取盐和算法参数
        3. 支持多种 bcrypt 变体（2a, 2b, 2y）
        
    Example:
        >>> is_valid = verify_password("mysecret", "$2b$12$...")
        >>> print(is_valid)  # True or False
    """
    try:
        # 将密码和哈希值转换为字节
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # 验证密码
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        # 任何异常都返回 False，避免信息泄露
        return False
