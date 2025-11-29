from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime  # 必须导入 datetime

# 导入我们自己写的文件
from app.database import get_db
from app import models, schemas
from app.models import User, Book, Word, UserWordProgress

# 初始化应用
app = FastAPI(
    title="English Learning Agent API",
    description="英语大模型助教后端接口",
    version="0.0.1"
)

# --- 临时辅助函数：模拟获取当前登录用户 ---
# 在真正的项目中，这里会从 Token 解析出 user_id
async def get_current_user_id():
    return 1  # 假设当前一直是 ID=1 的用户在操作

# --- 辅助函数：伪造的密码加密 ---
def fake_hash_password(password: str):
    return password + "notreallyhashed"

# =======================
# 基础路由与健康检查
# =======================

@app.get("/")
async def root():
    return {"message": "Hello, English Learning Agent!", "status": "running"}

@app.get("/health")
async def health_check():
    return {"database": "checking...", "redis": "not_connected_yet"}

@app.get("/health/db")
async def test_db_connection(db: AsyncSession = Depends(get_db)):
    try:
        # 执行一个最简单的 SQL：SELECT 1
        result = await db.execute(text("SELECT 1"))
        return {
            "status": "success", 
            "message": "Database connected successfully!", 
            "result": result.scalar()
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Database connection failed: {str(e)}"
        }

# =======================
# 用户相关接口 (User)
# =======================

@app.post("/users/", response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    注册新用户：
    1. 检查邮箱是否已存在
    2. 加密密码
    3. 存入数据库
    """
    # 1. 查询邮箱是否存在
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    db_user = result.scalar_one_or_none()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. 准备数据库模型对象
    new_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=fake_hash_password(user.password)
    )
    
    # 3. 添加到会话并提交
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

# =======================
# 学习业务接口 (Study)
# =======================

@app.post("/study/progress", response_model=schemas.ProgressOut)
async def create_learning_record(
    progress_data: schemas.ProgressCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id) # 注入当前用户ID
):
    """
    用户开始学习一个新单词：
    1. 检查是否已经学过这个词
    2. 如果没学过 -> 创建新记录
    3. 如果学过 -> 返回现有记录
    """
    # 1. 查重：看看这个用户对这个词是不是已经有进度了
    stmt = select(UserWordProgress).where(
        UserWordProgress.user_id == user_id,
        UserWordProgress.word_id == progress_data.word_id
    )
    result = await db.execute(stmt)
    existing_record = result.scalar_one_or_none()

    if existing_record:
        # 如果已经有了，直接返回旧的记录
        return existing_record

    # 2. 创建新记录
    # 注意：next_review_at 设置为当前时间，表示"现在就需要复习/学习"
    new_progress = UserWordProgress(
        user_id=user_id,
        word_id=progress_data.word_id,
        proficiency=0,
        next_review_at=datetime.now() 
    )

    # 3. 写入数据库
    db.add(new_progress)
    await db.commit()
    await db.refresh(new_progress)

    return new_progress