from fastapi import APIRouter
from .user.user import router as user_router

# 创建API路由器
internal_router = APIRouter(prefix="/internal",tags=["内部接口"])


# 添加路由器到内部路由器
internal_router.include_router(user_router)





