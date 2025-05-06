import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from TORTOISE_ORM import TORTOISE_ORM

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # 基础配置
    PROJECT_NAME = "FastAPI应用"
    PROJECT_DESCRIPTION = "使用FastAPI构建的后端API"
    VERSION = "1.0.0"

    # 数据库配置
    DATABASE_CONFIG = TORTOISE_ORM

    # JWT配置
    SECRET_KEY = os.getenv("SECRET_KEY", "default-fallback-secret-key-CHANGE-ME")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1280))
    ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
    LOG_RETENTION = os.getenv("LOG_RETENTION", "30 days")
    LOG_ROTATION = os.getenv("LOG_ROTATION", "00:00")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}")
    LOG_COMPRESS = os.getenv("LOG_COMPRESS", "True").lower() == "true"

    # CORS配置
    raw_origins = os.getenv("CORS_ORIGINS", "*")
    CORS_ORIGINS = [origin.strip() for origin in raw_origins.split(',')] if raw_origins != "*" else ["*"]
    CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "True").lower() == "true"
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]

class DevelopmentConfig(Config):
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "INFO"
    raw_origins = os.getenv("CORS_ORIGINS", "https://yourfrontend.com,https://another.domain.com")
    CORS_ORIGINS = [origin.strip() for origin in raw_origins.split(',')]
    if Config.SECRET_KEY == "default-fallback-secret-key-CHANGE-ME":
         print("CRITICAL WARNING: SECRET_KEY is not set in production environment variables!")

def get_config():
    env = os.getenv("FASTAPI_ENV", "development").lower()
    print(f"--- Loading configuration for environment: {env} ---")
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()

config = get_config()

# Example: You can now access config.DATABASE_CONFIG and it will have values loaded from .env
# print(config.DATABASE_CONFIG['connections']['default']['credentials']['host'])
# print(config.SECRET_KEY)