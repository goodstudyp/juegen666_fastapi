from fastapi import APIRouter, Query, UploadFile, File
from schemas.internal.user import LoginRequest
from schemas.Baseresponse import success_response, error_response
from core.jwtwoken import create_access_token
from utils.crypto import PasswordManager
from core.loguru import logger
from model.enum.user import UserStatus, UserType
from model.user import User
from schemas.internal.user import CreateUserRequest, UserListItem, UpdateUserRequest
from core.Exception import DatabaseException
from typing import Optional
from common.pagination import get_paginated_response
from fastapi import Depends
from core.auth import get_admin_user
from datetime import datetime
import os
import shutil


# 创建API路由器
router = APIRouter(prefix="/users", tags=["内部用户管理"])

@router.post("/login")
async def login_user(login_data: LoginRequest):
    """
    用户登录接口
    
    Args:
        login_data: 登录请求数据，包含用户名和密码
        
    Returns:
        包含token和用户信息的响应
    """
    try:
        logger.debug(f"用户尝试登录: {login_data.username}")
        
        # 查找用户
        user = await User.filter(username=login_data.username).first()
        
        if not user:
            logger.warning(f"登录失败: 用户名 {login_data.username} 不存在")
            return error_response("用户名或密码错误")
        
        # 验证密码
        if not PasswordManager.verify(login_data.password, user.password):
            logger.warning(f"登录失败: 用户 {login_data.username} 密码错误")
            return error_response("用户名或密码错误")
        
        # 检查用户状态
        if user.user_status != UserStatus.ACTIVE:
            logger.warning(f"登录失败: 用户 {login_data.username} 已被禁用")
            return error_response("用户已被禁用")
        
        if user.user_type != UserType.ADMIN and user.user_type != UserType.SUPER_ADMIN:
            logger.warning(f"登录失败: 用户 {login_data.username} 不是管理员")
            return error_response("用户不是管理员")
        
        # 创建访问令牌
        access_token = create_access_token(user_id=user.id, user_type=user.user_type)
        logger.info(f"用户 {user.username} 登录成功")
        
        # 更新登录时间
        user.login_time = datetime.now()
        await user.save()
        
        # 返回令牌和用户信息
        return success_response(
            message="登录成功",
            data=access_token    
        )
    except Exception as e:
        error_msg = f"登录处理时发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_response(error_msg)



@router.post("/create_user")
async def create_user(user_data: CreateUserRequest):
    """
    创建用户
    
    Args:
        user_data: 用户创建请求数据，包含用户名、密码、邮箱、手机号、昵称、性别、备注、用户类型、用户状态
        
    Returns:
        包含创建结果的响应
    """
    try:
        logger.debug(f"创建用户: {user_data.username}") 

        # 检查用户是否已存在
        existing_user = await User.filter(username=user_data.username).first()
        if existing_user:
            logger.warning(f"创建用户失败: 用户名 {user_data.username} 已存在")
            return error_response("用户名已存在")
        
        # 创建用户
        user = await User.create(
            username=user_data.username,
            password=PasswordManager.hash(user_data.password),
            user_email=user_data.user_email,
            user_phone=user_data.user_phone,      
            nickname=user_data.nickname,
            sex=user_data.sex,
            remarks=user_data.remarks,
            user_type=user_data.user_type,
            user_status=user_data.user_status,
        )
        
        logger.info(f"用户 {user.username} 创建成功")
        
        # 转换为 UserListItem 格式返回
        return success_response(
            message="用户创建成功"
        )
    except Exception as e:
        error_msg = f"创建用户时发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_response(error_msg)


@router.get("/get_user_info/{user_id}",dependencies=[Depends(get_admin_user)])
async def get_user(user_id: int):
    """
    获取用户详情
    
    Args:
        user_id: 用户ID
        
    Returns:
        包含用户详情的响应
    """
    try:
        user = await User.get(id=user_id)
        return success_response(
           message="获取用户详情成功",
           data=UserListItem(
               id=user.id,
               username=user.username,
               nickname=user.nickname,
               email=user.user_email,
               phone=user.user_phone,
               user_type=user.user_type,
               user_status=user.user_status,
               avatar=user.avatar
           )
        )
   
    except Exception as e:
        logger.error(f"获取用户详情失败: {e}")
        raise DatabaseException(detail=f"获取用户详情失败: {e}")


@router.put("/update_user/{user_id}", dependencies=[Depends(get_admin_user)])
async def update_user(user_id: int, user_data: UpdateUserRequest):
    """
    更新用户信息
    
    Args:
        user_id: 用户ID
        user_data: 用户更新请求数据，包含用户名、密码、邮箱、手机号、昵称、性别、备注、用户类型、用户状态
        
    Returns:
        包含更新结果的响应
    """
    try:
        logger.debug(f"更新用户: {user_id}")

        # 检查用户是否存在
        user = await User.get(id=user_id)
        if not user:
            logger.warning(f"更新用户失败: 用户ID {user_id} 不存在")
            return error_response("用户不存在")
        
        # 更新用户信息
        user.username = user_data.username
        user.user_email = user_data.user_email
        user.user_phone = user_data.user_phone
        user.nickname = user_data.nickname
        user.sex = user_data.sex
        user.remarks = user_data.remarks
        user.user_type = user_data.user_type
        user.user_status = user_data.user_status
        user.client_host = user_data.client_host
        await user.save()
        
        logger.info(f"用户 {user.username} 更新成功")
        
        return success_response(
            message="用户更新成功",
            data=UserListItem(
                id=user.id,
                username=user.username,
                nickname=user.nickname,
                user_type=user.user_type,
                user_status=user.user_status,
                user_phone=user.user_phone,
                user_email=user.user_email,
                avatar=user.avatar
            )
        )
    except Exception as e:
        error_msg = f"更新用户时发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_response(error_msg)


@router.delete("/delete_user/{user_id}", dependencies=[Depends(get_admin_user)])
async def delete_user(user_id: int):
    """
    删除用户
    
    Args:
        user_id: 用户ID
        
    Returns:
        包含删除结果的响应
    """
    try:
        user = await User.get(id=user_id)
        if not user:
            logger.warning(f"删除用户失败: 用户ID {user_id} 不存在")
            return error_response("用户不存在")
        
        await user.delete()
        
        logger.info(f"用户 {user.username} 删除成功")
        
        return success_response(
            message="用户删除成功"
        )
    except Exception as e:
        error_msg = f"删除用户时发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_response(error_msg)

@router.get("/get_user_list", dependencies=[Depends(get_admin_user)])
async def get_user_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    username: Optional[str] = Query(None, description="用户名过滤"),
    nickname: Optional[str] = Query(None, description="昵称过滤"),
    user_type: Optional[int] = Query(None, description="用户类型过滤"),
    user_status: Optional[int] = Query(None, description="用户状态过滤"),
    user_phone: Optional[str] = Query(None, description="手机号过滤"),
    user_email: Optional[str] = Query(None, description="邮箱过滤"),
    sex: Optional[int] = Query(None, description="性别过滤")
):
    """
    获取用户列表
    
    Args:
        page: 当前页码 
        page_size: 每页条数
        username: 用户名过滤
        nickname: 昵称过滤
        user_type: 用户类型过滤
        user_status: 用户状态过滤
        user_phone: 手机号过滤
        user_email: 邮箱过滤
        sex: 性别过滤

    Returns:
        包含用户列表的响应
    """
    try:
        # 构建查询集
        query = User.all()
        
        # 构建过滤条件
        filters = {}
        if username:
            filters["username__contains"] = username
        if nickname:
            filters["nickname__contains"] = nickname
        if user_type is not None:
            filters["user_type"] = user_type
        if user_status is not None:
            filters["user_status"] = user_status
        if user_phone:
            filters["user_phone__contains"] = user_phone
        if user_email:
            filters["user_email__contains"] = user_email
        if sex is not None:
            filters["sex"] = sex
        
        # 使用通用分页响应函数获取分页结果
        pagination_result = await get_paginated_response(
            query_set=query,
            page=page,
            page_size=page_size,
            schema_model=UserListItem,
            filters=filters
        )
        
        return success_response(
            message="用户列表获取成功",
            data=pagination_result
        )
    except Exception as e:
        error_msg = f"获取用户列表时发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_response(error_msg)

@router.post("/upload_avatar/{user_id}")
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_admin_user)
):
    """
    上传用户头像
    
    Args:
        user_id: 用户ID
        file: 上传的图片文件
        current_user: 当前登录用户
        
    Returns:
        包含头像URL的响应
    """
    try:
        # 检查文件类型
        user = await User.get(id=user_id)
        if not user:
            return error_response("用户不存在")
        allowed_types = ["image/jpeg", "image/png", "image/gif"]
        if file.content_type not in allowed_types:
            return error_response("只允许上传 JPG、PNG 或 GIF 格式的图片")
        
        # 创建保存目录
        avatar_dir = "static/avatars"
        os.makedirs(avatar_dir, exist_ok=True)
        
        # 生成文件名 (用户ID + 原始文件扩展名)
        file_extension = os.path.splitext(file.filename)[1]
        avatar_name = f"{user_id}{file_extension}"
        file_path = os.path.join(avatar_dir, avatar_name)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 更新用户头像字段
        avatar_url = f"/static/avatars/{avatar_name}"
        user.avatar = avatar_url
        await user.save()
        
        logger.info(f"用户 {user.username} 更新头像成功")
        
        return success_response(
            message="头像上传成功",
            data={"avatar_url": avatar_url}
        )
    except Exception as e:
        error_msg = f"头像上传失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_response(error_msg)
    finally:
        file.file.close()















