#/home/btls/english-learning-agent/backend/app/main.py
# /home/btls/english-learning-agent/backend/app/main.py
from app.api import chat
import asyncio
from logging.config import fileConfig
import os
import sys
from datetime import datetime, timedelta
from typing import List
import math
# 1. FastAPI 相关
# 【修复点 1】：这里加上了 status
from fastapi import FastAPI, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# 2. 数据库相关
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

# 3. JWT 相关
# 【修复点 2】：这一行之前漏掉了，必须加上，否则无法解密 Token
from jose import JWTError, jwt 

# 4. 本地模块
from app.database import get_db
from app import models, schemas
from app.models import User, Book, Word, UserWordProgress
# 引入密钥配置，用于解密
from app.security import (
    verify_password, 
    create_access_token, 
    get_password_hash,
    SECRET_KEY, 
    ALGORITHM
)
# 引入依赖函数
from app.dependencies import get_current_user

# 初始化应用
app = FastAPI(
    title="English Learning Agent API",
    description="英语大模型助教后端接口",
    version="0.0.1"
)

app.include_router(chat.router)



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
    注册新用户
    """
    # 1. 查询邮箱是否存在
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    db_user = result.scalar_one_or_none()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. 准备数据库模型对象
    # 【修改点】：使用 get_password_hash 替代 fake_hash_password
    new_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password) # <--- 这里改了
    )
    
    # 3. 添加到会话并提交
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录接口 (获取 Token)
    注意：虽然 form_data 里的字段叫 username，但我们逻辑上是把它当 email 用
    """
    try:
        # 1. 尝试在数据库中查找用户 (按邮箱查找)
        # 这里的 form_data.username 是前端传来的账号（在这个系统里是邮箱）
        stmt = select(models.User).where(models.User.email == form_data.username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        # 2. 验证用户是否存在，以及密码是否正确
        # verify_password(明文, 密文) -> bool
        if not user or not verify_password(form_data.password, user.hashed_password):
            # 401 Unauthorized 是标准的认证失败状态码
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. 登录成功，生成 Token
        # 我们把 email 放入 Token 中，作为身份标识 (sub)
        access_token_expires = timedelta(minutes=30) # 30分钟有效期，也可以去读 .env 配置
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )

        # 4. 返回 Token 给前端
        return {"access_token": access_token, "token_type": "bearer"}
    
    except HTTPException:
        # 重新抛出HTTP异常（如401）
        raise
    except Exception as e:
        # 捕获其他异常，返回详细错误信息用于调试
        import traceback
        error_detail = f"登录处理失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


# =======================
# 学习业务接口 (Study)
# =======================

@app.post("/study/progress", response_model=schemas.ProgressOut)
async def create_learning_record(
    progress_data: schemas.ProgressCreate,
    db: AsyncSession = Depends(get_db),
    # 【修改这里】：依赖变成了 get_current_user，类型是 models.User
    current_user: models.User = Depends(get_current_user) 
):
    # 下面的 user_id 都要改成 current_user.id
    
    # 1. 查重
    stmt = select(UserWordProgress).where(
        UserWordProgress.user_id == current_user.id, # <--- 修改
        UserWordProgress.word_id == progress_data.word_id
    )
    result = await db.execute(stmt)
    existing_record = result.scalar_one_or_none()

    if existing_record:
        return existing_record

    # 2. 创建新记录
    new_progress = UserWordProgress(
        user_id=current_user.id, # <--- 修改
        word_id=progress_data.word_id,
        proficiency=0,
        next_review_at=datetime.now() 
    )

    db.add(new_progress)
    await db.commit()
    await db.refresh(new_progress)

    return new_progress

@app.get("/study/needs-review", response_model=List[schemas.ProgressWithWord])
async def get_words_to_review(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # <--- 修改
):
    now = datetime.now()
    stmt = (
        select(UserWordProgress)
        .options(selectinload(UserWordProgress.word))
        .where(
            UserWordProgress.user_id == current_user.id, # <--- 修改
            UserWordProgress.next_review_at <= now
        )
        .order_by(UserWordProgress.next_review_at)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@app.post("/study/review", response_model=schemas.ProgressOut) # 注意这里改了 response_model
async def review_word(
    review_data: schemas.ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    SuperMemo-2 (SM-2) 算法实现接口
    输入: word_id, quality (0-5)
    输出: 更新后的进度记录
    """
    # 1. 查找进度记录
    stmt = select(UserWordProgress).where(
        UserWordProgress.user_id == current_user.id,
        UserWordProgress.word_id == review_data.word_id
    )
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    # 如果还没学过这个词，就先创建一条进度（容错处理）
    if not progress:
        progress = UserWordProgress(
            user_id=current_user.id,
            word_id=review_data.word_id,
            easiness_factor=2.5,
            interval=0,
            repetitions=0
        )
        db.add(progress)

    # 2. 提取当前状态
    q = review_data.quality
    ef = progress.easiness_factor
    reps = progress.repetitions
    interval = progress.interval

    # 3. 运行 SM-2 算法
    if q < 3:
        # --- 失败分支 ---
        # 如果忘了 (0-2分)，进度重置
        reps = 0
        interval = 1 
        # EF 保持不变 (有些变体建议减少 EF，但原版 SM-2 只有成功才调整 EF，这里我们简化处理)
    else:
        # --- 成功分支 ---
        # A. 计算新的 EF
        # 公式：EF' = EF + (0.1 - (5-q) * (0.08 + (5-q)*0.02))
        # 逻辑：打分越低(接近3)，减分越多
        new_ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        if new_ef < 1.3:
            new_ef = 1.3 # 设定下限，防止死循环
        ef = new_ef

        # B. 计算新的间隔 (Interval)
        reps += 1
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 6
        else:
            # 第三次及以后：旧间隔 * EF
            interval = int(interval * ef)

    # 4. 更新数据库对象
    progress.easiness_factor = ef
    progress.repetitions = reps
    progress.interval = interval
    
    # 5. 计算下次复习的具体日期
    now = datetime.now()
    progress.last_reviewed_at = now
    progress.next_review_at = now + timedelta(days=interval)
    
    # 更新熟练度 (仅作 UI 展示，非算法核心)
    # 简单逻辑：连续对的次数越多，熟练度越高，封顶 100
    progress.proficiency = min(reps * 20, 100)

    # 6. 提交事务
    await db.commit()
    await db.refresh(progress)
    
    return progress