import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "a1527896724")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_ENGINE = os.getenv("DB_ENGINE", "tortoise.backends.asyncpg")

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': DB_ENGINE,
            'credentials': {
                'host': DB_HOST,
                'port': DB_PORT,
                'user': DB_USER,
                'password': DB_PASSWORD,
                'database': DB_NAME,
            }
        }
    },
    'apps': {
        'models': {
            'models': ["model", "aerich.models"],
            'default_connection': 'default',
        }
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai'
} 