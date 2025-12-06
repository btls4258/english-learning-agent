# backend/app/api/main.py
"""
API路由主配置文件 - 统一管理所有API路由
"""
from fastapi import APIRouter

# 导入各个模块的路由
from . import auth, chat, study, books

# 创建主路由器
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(study.router, tags=["study"])
api_router.include_router(books.router, tags=["books"])

# 为了向后兼容，也提供直接的router引用
router = api_router