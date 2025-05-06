from fastapi import Request
import time
from core.loguru import app_logger as logger
from model.operation_log import OperationLog
from tortoise.exceptions import OperationalError
from core.jwtwoken import verify_token
from fastapi import HTTPException
from config import config
from fastapi import FastAPI

async def log_internal_requests(request: Request, call_next):
    """
    专门用于记录内部API请求的中间件
    只对以/api/internal/开头的请求路径生效
    """
    # 检查是否是内部接口
    is_internal_api = request.url.path.startswith("/api/internal/")
    
    # 如果不是内部接口，直接调用下一个处理器
    if not is_internal_api:
        return await call_next(request)
    
    # 不记录日志的路径列表
    skip_log_paths = [
        "/api/internal/users/get_user_list"
    ]
    
    # 检查是否是需要跳过记录的路径
    path_without_query = request.url.path.split("?")[0]
    if path_without_query in skip_log_paths:
        # 直接调用下一个处理器，不记录日志
        return await call_next(request)
    
    # 对内部接口进行日志记录
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"开始请求: {request.method} {request.url.path}")
    
    try:
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = (time.time() - start_time) * 1000
        logger.info(f"完成请求: {request.method} {request.url.path} - 状态码: {response.status_code} - 处理时间: {process_time:.2f}ms")
        
        # 对于OPTIONS请求，只记录到控制台，不记录到数据库
        if request.method == "OPTIONS":
            return response
        
        # 记录操作日志到数据库
        try:
            # 获取用户信息
            user_id = None
            username = "system"  # 默认使用system作为用户名，而不是unknown
            
            # 从请求头中获取token
            token = None
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
            
            # 如果找到token，尝试解析
            if token:
                try:
                    # 使用verify_token获取用户信息
                    token_data = verify_token(token)
                    if token_data:
                        from model.user import User
                        # 获取用户详细信息
                        user = await User.filter(id=token_data.user_id).first()
                        if user:
                            user_id = user.id
                            username = user.username
                except Exception as token_err:
                    logger.warning(f"解析Token失败: {str(token_err)}")
            
            # 操作结果
            result = "成功" if response.status_code < 400 else "失败"
            
            # 写入数据库 - 只有当user_id不为None时才写入
            if user_id is not None:
                await OperationLog.create(
                    user_id=user_id,
                    username=username,
                    operation=f"{request.method} {request.url.path}",
                    result=result
                )
            else:
                # 记录无法写入数据库的情况
                logger.info(f"跳过记录日志到数据库: 无法获取用户ID, 路径: {request.url.path}")
        except OperationalError as e:
            logger.error(f"记录操作日志到数据库失败: {str(e)}")
        
        return response
    except Exception as e:
        # 捕获中间件中的异常
        process_time = (time.time() - start_time) * 1000
        logger.error(f"请求处理异常: {request.method} {request.url.path} - 异常: {str(e)} - 处理时间: {process_time:.2f}ms")
        
        # 对于OPTIONS请求，只记录到控制台，不记录到数据库
        if request.method == "OPTIONS":
            raise  # 重新抛出异常，让异常处理器处理
        
        # 记录操作日志到数据库 - 异常情况
        try:
            # 获取用户信息
            user_id = None
            username = "system"  # 默认使用system作为用户名
            
            # 从请求头中获取token
            token = None
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
            
            # 如果找到token，尝试解析
            if token:
                try:
                    # 使用verify_token获取用户信息
                    token_data = verify_token(token)
                    if token_data:
                        from model.user import User
                        # 获取用户详细信息
                        user = await User.filter(id=token_data.user_id).first()
                        if user:
                            user_id = user.id
                            username = user.username
                except Exception as token_err:
                    logger.warning(f"解析Token失败: {str(token_err)}")
            
            # 写入数据库 - 只有当user_id不为None时才写入
            if user_id is not None:
                await OperationLog.create(
                    user_id=user_id,
                    username=username,
                    operation=f"{request.method} {request.url.path}",
                    result=f"异常: {str(e)}"
                )
            else:
                # 记录无法写入数据库的情况
                logger.info(f"跳过记录异常日志到数据库: 无法获取用户ID, 路径: {request.url.path}")
        except Exception as db_err:
            logger.error(f"记录异常操作日志到数据库失败: {str(db_err)}")
        
        raise  # 重新抛出异常，让异常处理器处理


async def log_operation(request: Request, call_next):
    """
    通用操作日志中间件，记录所有API请求到数据库
    """
    # 排除静态资源、文档等路径
    if request.url.path.startswith(("/docs", "/redoc", "/static", "/openapi.json")):
        return await call_next(request)
    
    start_time = time.time()
    
    try:
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = (time.time() - start_time) * 1000
        
        # 获取用户信息
        user_id = None
        username = "unknown"
        
        # 从请求头中获取token
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header
        else:
            raise HTTPException(status_code=401, detail="未授权")
        
        # 如果找到token，尝试解析
        if token:
            try:
                # 使用verify_token获取用户信息
                token_data = verify_token(token)
                if token_data:
                    from model.user import User
                    # 获取用户详细信息
                    user = await User.filter(id=token_data.user_id).first()
                    if user:
                        user_id = user.id
                        username = user.username
            except Exception as token_err:
                logger.warning(f"解析Token失败: {str(token_err)}")
        
        # 操作结果
        result = "成功" if response.status_code < 400 else "失败"
        
        # 写入数据库
        await OperationLog.create(
            user_id=user_id,
            username=username,
            operation=f"{request.method} {request.url.path}",
            result=result
        )
        
        return response
    except Exception as e:
        # 捕获中间件中的异常
        process_time = (time.time() - start_time) * 1000
        
        # 尝试记录异常到数据库
        try:
            # 获取用户信息
            user_id = None
            username = "unknown"
            
            # 从请求头中获取token
            token = None
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
            
            # 如果找到token，尝试解析
            if token:
                try:
                    # 使用verify_token获取用户信息
                    token_data = verify_token(token)
                    if token_data:
                        from model.user import User
                        # 获取用户详细信息
                        user = await User.filter(id=token_data.user_id).first()
                        if user:
                            user_id = user.id
                            username = user.username
                except Exception as token_err:
                    logger.warning(f"解析Token失败: {str(token_err)}")
            
            # 写入数据库
            await OperationLog.create(
                user_id=user_id,
                username=username,
                operation=f"{request.method} {request.url.path}",
                result=f"异常: {str(e)}"
            )
        except Exception as db_err:
            logger.error(f"记录操作日志失败: {str(db_err)}")
        
        raise  # 重新抛出异常


# Register application middleware and event handlers
def register_middleware(app: FastAPI):
    """注册应用中间件"""
    from fastapi.middleware.cors import CORSMiddleware
    from middleware import log_internal_requests
    
    # 注册CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=config.CORS_CREDENTIALS,
        allow_methods=config.CORS_METHODS,
        allow_headers=config.CORS_HEADERS,
    )
    
    # 注册内部API日志中间件
    app.middleware("http")(log_internal_requests)
    logger.info("已注册内部API日志中间件")