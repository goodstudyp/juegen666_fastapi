from fastapi import APIRouter
from .internal import internal_router

# 创建API路由器
api_router = APIRouter()


# 添加内部路由器到API路由器
api_router.include_router(internal_router)




