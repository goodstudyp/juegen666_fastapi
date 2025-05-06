from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from tortoise import Tortoise
from config import config
from core.loguru import logger
import importlib
import inspect


async def init_db(app: FastAPI) -> None:
    """
    初始化数据库连接
    """
    try:
        # 首先检查model目录下是否有可用的模型类
        try:
            import model
            import model.user  # 尝试导入用户模型
            from model.user import User  # 尝试导入User模型类
            logger.info(f"成功导入User模型: {User}")
            model_classes = inspect.getmembers(model.user, inspect.isclass)
            tortoise_models = [cls for name, cls in model_classes if hasattr(cls, '_meta')]
            logger.info(f"找到Tortoise ORM模型类: {tortoise_models}")
        except ImportError as e:
            logger.error(f"导入模型失败: {e}")
        
        # 打印Tortoise配置信息
        db_config = config.DATABASE_CONFIG.copy()
        # 隐藏密码
        if 'credentials' in db_config['connections']['default']:
            db_config['connections']['default']['credentials'] = {
                **db_config['connections']['default']['credentials'],
                'password': '******'  # 隐藏密码
            }
        logger.info(f"Tortoise配置: {db_config}")
        
        # 使用register_tortoise方法初始化数据库连接
        logger.info("使用register_tortoise初始化数据库连接...")
        register_tortoise(
            app,
            config=config.DATABASE_CONFIG,
            generate_schemas=True,  # 自动创建数据表
            add_exception_handlers=True,  # 添加异常处理
        )
        
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        # 更详细的错误信息记录
        logger.exception("数据库初始化详细错误")
        raise


async def close_db() -> None:
    """
    关闭数据库连接
    """
    try:
        from tortoise import Tortoise
        if Tortoise._inited:
            await Tortoise.close_connections()
            logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {str(e)}")
        raise


async def get_db_version():
    """
    获取数据库版本信息
    """
    try:
        from tortoise import Tortoise
        conn = Tortoise.get_connection("default")
        result = await conn.execute_query("SELECT version()")
        version = result[1][0]["version"] if result and len(result) > 1 else None
        logger.debug(f"获取数据库版本成功: {version}")
        return version
    except Exception as e:
        logger.error(f"获取数据库版本失败: {str(e)}")
        raise

