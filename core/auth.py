from fastapi import Depends
from core.jwtwoken import TokenPayload, verify_token
from fastapi.security import OAuth2PasswordBearer
from model.user import User
from model.enum.user import UserType
from core.Exception import (
    NotFoundException,
    ForbiddenException,
    BadRequestException
)
from core.loguru import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    """
    依赖项：获取当前用户信息
    
    Args:
        token: JWT token (由FastAPI自动从请求头中提取)
        
    Returns:
        当前用户的TokenPayload对象
        
    Raises:
        BadRequestException: 当token验证失败时
    """
    try:
        token_payload = verify_token(token)
        return token_payload
    except Exception as e:
        logger.warning(f"无效的身份认证凭据: {str(e)}")
        raise BadRequestException(detail="无效的身份认证凭据")


async def get_current_active_user(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    """
    依赖项：获取当前活跃用户
    检查用户是否被禁用
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        当前用户的TokenPayload对象
        
    Raises:
        NotFoundException: 当用户不存在时
        ForbiddenException: 当用户被禁用时
    """
    # 从数据库获取用户详细信息
    user = await User.filter(id=current_user.user_id).first()
    if not user:
        logger.warning(f"用户不存在: user_id={current_user.user_id}")
        raise NotFoundException(detail=f"用户不存在: ID={current_user.user_id}")
    
    # 检查用户状态
    if user.user_status != 1:  # 1为正常状态
        logger.warning(f"用户已被禁用: user_id={current_user.user_id}")
        raise ForbiddenException(detail="用户已被禁用")
    
    return current_user


async def get_admin_user(current_user: TokenPayload = Depends(get_current_active_user)) -> TokenPayload:
    """
    依赖项：获取管理员用户
    检查用户是否拥有管理员权限
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        当前用户的TokenPayload对象
        
    Raises:
        ForbiddenException: 当用户无管理员权限时
    """
    # 从数据库获取用户详细信息，确保权限信息是最新的
    user = await User.filter(id=current_user.user_id).first()
    
    # 检查用户类型
    if user.user_type not in [UserType.ADMIN, UserType.SUPER_ADMIN]:
        logger.warning(f"权限不足: user_id={current_user.user_id}, user_type={user.user_type}")
        raise ForbiddenException(detail="权限不足，需要管理员权限")
    
    return current_user


async def get_super_admin_user(current_user: TokenPayload = Depends(get_current_active_user)) -> TokenPayload:
    """
    依赖项：获取超级管理员用户
    检查用户是否拥有超级管理员权限
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        当前用户的TokenPayload对象
        
    Raises:
        ForbiddenException: 当用户无超级管理员权限时
    """
    # 从数据库获取用户详细信息，确保权限信息是最新的
    user = await User.filter(id=current_user.user_id).first()
    
    # 检查用户类型
    if user.user_type != UserType.SUPER_ADMIN:
        logger.warning(f"权限不足: user_id={current_user.user_id}, user_type={user.user_type}")
        raise ForbiddenException(detail="权限不足，需要超级管理员权限")
    
    return current_user


