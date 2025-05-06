from contextlib import asynccontextmanager
from fastapi import FastAPI
import time
import os
from pathlib import Path

# Import database and logging modules
from database.pgsql import init_db, close_db
from core.loguru import app_logger as logger
from config import config
from api import api_router
from core.Exception import DatabaseException, InternalServerErrorException

async def check_db_connection():
    """
    检查数据库连接是否可用，使用自定义异常处理
    
    Raises:
        DatabaseException: 当数据库连接失败时抛出
        InternalServerErrorException: 当发生其他内部错误时抛出
    """
    try:
        # 尝试初始化数据库连接
        app = FastAPI()
        await init_db(app)
        
        # 如果成功连接，关闭连接
        await close_db()
        logger.info("数据库连接检查成功")
        return True
        
    except Exception as e:
        error_msg = f"数据库连接检查失败: {str(e)}"
        logger.error(error_msg)
        
        if "database" in str(e).lower():
            raise DatabaseException(detail=error_msg)
        else:
            raise InternalServerErrorException(detail=error_msg)
            
    finally:
        try:
            await close_db()
        except Exception as e:
            logger.warning(f"关闭数据库连接时出现警告: {str(e)}")

# Check and create necessary directories
def ensure_directories():
    """确保应用所需的目录存在"""
    # 日志目录
    if not os.path.exists(config.LOG_DIR):
        Path(config.LOG_DIR).mkdir(parents=True, exist_ok=True)
        logger.info(f"创建日志目录: {config.LOG_DIR}")
    
    # 上传文件目录
    static_dir = Path("static")
    if not static_dir.exists():
        static_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"创建上传目录: {static_dir}")


# Log system information
def log_system_info():
    """记录系统信息"""
    import platform
    import sys
    
    # 获取当前环境
    env = os.getenv("FASTAPI_ENV", "development")
    
    logger.info(f"系统信息: {platform.system()} {platform.release()} ({platform.version()})")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"运行环境: {env}")
    logger.info(f"调试模式: {'启用' if config.DEBUG else '禁用'}")





# FastAPI lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI应用的生命周期管理
    在应用启动时初始化资源，在应用关闭时释放资源
    """
    # 应用启动前执行的操作
    logger.info("=== 应用启动 ===")
    logger.info(f"应用名称: {config.PROJECT_NAME} v{config.VERSION}")
    
    # 确保目录存在
    ensure_directories()
    # 记录系统信息
    log_system_info()

    # 注册API路由
    app.include_router(api_router, prefix="/api")
    logger.info("API路由注册成功")
    
    # 初始化数据库
    try:
        # init_db现在是异步函数，需要使用await
        await init_db(app)
        logger.info("数据库连接初始化成功")
    except Exception as e:
        logger.error(f"数据库连接初始化失败: {str(e)}")
        # 严重错误，无法继续运行，记录错误并抛出异常
        logger.critical("应用无法正常启动，请检查数据库配置")
        raise
    
    # 其他初始化操作
    logger.info("所有资源初始化完成")
    logger.info("=== 应用启动完成 ===")
    
    yield  # 此处FastAPI接管，处理请求
    
    # 应用关闭时执行的操作
    logger.info("=== 应用正在关闭 ===")
    
    # 关闭数据库连接
    try:
        await close_db()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接时出错: {str(e)}")
    
    # 清理其他资源
    logger.info("所有资源已释放")
    logger.info("=== 应用已关闭 ===")


# 使用方法说明:
# 在main.py中引入并使用:
# from core.lifespan import lifespan
#
# app = FastAPI(lifespan=lifespan)
