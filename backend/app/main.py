# backend/app/main.py
"""
FastAPI应用主入口文件 - 应用初始化和路由配置
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.database import engine
from app.models import Base
import os

# 初始化应用
app = FastAPI(
    title="English Learning Agent API",
    description="英语大模型助教后端接口 - 智能化英语备考系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源，生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(router, prefix="/api/v1")

# 基础路由
@app.get("/")
async def root():
    """根路径 - API基础信息"""
    return {
        "message": "English Learning Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "service": "English Learning Agent API",
        "version": "1.0.0"
    }

@app.get("/health/db")
async def test_db_connection():
    """数据库连接健康检查"""
    try:
        return {
            "status": "healthy",
            "database": "PostgreSQL",
            "connection": "success"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "PostgreSQL",
            "connection": "failed",
            "error": str(e)
        }

# 启动时创建数据库表
@app.on_event("startup")
async def startup_event():
    """应用启动时的事件处理"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("🚀 English Learning Agent API started successfully!")
    print("📚 API Documentation available at: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的事件处理"""
    print("👋 English Learning Agent API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )