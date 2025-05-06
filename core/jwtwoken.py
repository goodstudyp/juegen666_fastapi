from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from config import config
from core.loguru import logger

# Token获取方式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Token负载模型
class TokenPayload(BaseModel):
    user_id: int
    user_type: int
    exp: Optional[datetime] = None


def create_token(user_id: int, user_type: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT Token
    
    Args:
        user_id: 用户ID
        user_type: 用户类型
        expires_delta: 过期时间增量
        
    Returns:
        生成的token字符串
    """
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + config.ACCESS_TOKEN_EXPIRE
    
    # 构建payload
    payload = {
        "user_id": user_id,
        "user_type": user_type,
        "exp": expire
    }
    
    # 编码并返回token
    try:
        encoded_jwt = jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"创建JWT Token失败: {str(e)}")
        raise


def create_access_token(user_id: int, user_type: int) -> Dict[str, str]:
    """
    创建访问令牌
    
    Args:
        user_id: 用户ID
        user_type: 用户类型
        
    Returns:
        包含token的字典
    """
    token = create_token(user_id, user_type, expires_delta=config.ACCESS_TOKEN_EXPIRE)
    return token


def verify_token(token: str) -> TokenPayload:
    """
    验证JWT Token
    
    Args:
        token: JWT token
        
    Returns:
        解析后的token payload
        
    Raises:
        HTTPException: 当token无效或已过期时
    """
    try:
        # 解码token
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        
        # 获取用户ID和类型
        user_id = payload.get("user_id")
        user_type = payload.get("user_type")
        
        # 验证必要字段是否存在
        if user_id is None or user_type is None:
            logger.warning("验证Token失败: Token无效")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token无效",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 返回令牌负载
        token_data = TokenPayload(
            user_id=user_id,
            user_type=user_type,
            exp=datetime.fromtimestamp(payload.get("exp")) if "exp" in payload else None
        )
        return token_data
    
    except JWTError as e:
        # JWT解析错误
        logger.warning(f"验证Token失败: JWT解析错误 - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

