import sys
import os
from datetime import datetime
from loguru import logger
from pathlib import Path
from config import config


def setup_logger():
    """
    配置日志系统
    """
    # 移除默认的日志处理器
    logger.remove()
    
    # 创建日志目录
    config.LOG_DIR.mkdir(exist_ok=True)
    
    # 获取当前日期作为日志文件名的一部分
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # 添加控制台输出处理器 - 常规日志
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO" if not config.DEBUG else "DEBUG",
        colorize=True,
        backtrace=False,  # 关闭常规日志的堆栈跟踪
        diagnose=False
    )
    
    # 添加控制台错误处理器 - 只处理错误和更高级别，并显示完整堆栈
    logger.add(
        sys.stderr,
        format="<red>{time:YYYY-MM-DD HH:mm:ss.SSS}</red> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>\n{exception}",
        level="ERROR",
        colorize=True,
        backtrace=True,  # 开启错误日志的堆栈跟踪
        diagnose=True,   # 显示更详细的诊断信息
        filter=lambda record: record["level"].no >= logger.level("ERROR").no
    )
    
    # 添加文件输出处理器，记录所有日志
    logger.add(
        f"{config.LOG_DIR}/app_{current_date}.log",
        format=config.LOG_FORMAT,
        level=config.LOG_LEVEL,
        rotation=config.LOG_ROTATION,
        retention=config.LOG_RETENTION,
        compression="zip" if config.LOG_COMPRESS else None,
        enqueue=True
    )
    
    # 添加错误日志文件处理器，只记录错误和更高级别的日志
    logger.add(
        f"{config.LOG_DIR}/error_{current_date}.log",
        format=config.LOG_FORMAT,
        level="ERROR",
        rotation=config.LOG_ROTATION,
        retention=config.LOG_RETENTION,
        compression="zip" if config.LOG_COMPRESS else None,
        enqueue=True
    )
    
    return logger


# 创建全局日志实例
app_logger = setup_logger()

