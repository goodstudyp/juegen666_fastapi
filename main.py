from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import uvicorn
import traceback
from tortoise.contrib.fastapi import register_tortoise
# 导入数据模型和数据库配置
from core.loguru import logger
from config import config
from core.lifespan import lifespan
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse
from middleware.logger_middleware import register_middleware

# 创建FastAPI实例
app = FastAPI(
    title=config.PROJECT_NAME,
    description=config.PROJECT_DESCRIPTION,
    version=config.VERSION,
    lifespan=lifespan,
    debug=config.DEBUG  # 确保设置debug模式
)

# 在应用启动前注册中间件
register_middleware(app)
logger.info("中间件注册成功")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册数据库
register_tortoise(
    app,
    config=config.DATABASE_CONFIG,
    generate_schemas=False,  # 不自动生成数据库表，我们使用 Aerich 来管理迁移
    add_exception_handlers=False,  # 关闭自动异常处理，使用我们自定义的处理器
)


# 运行服务器（当直接运行此文件时）
if __name__ == "__main__":
    logger.info("启动服务器")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
