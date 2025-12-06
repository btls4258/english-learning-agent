# backend/app/api/study.py
"""
学习业务相关的API路由 - 词汇学习、进度管理、SM-2算法
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user

router = APIRouter(prefix="/study", tags=["study"])


@router.post("/progress", response_model=schemas.ProgressOut)
async def create_learning_record(
    progress_data: schemas.ProgressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    创建学习记录 - 当用户开始学习一个新单词时调用

    Args:
        progress_data: 学习进度创建数据
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        创建的学习进度记录

    Raises:
        HTTPException: 当单词ID无效时
    """
    # 1. 验证单词是否存在
    word_result = await db.execute(
        select(models.Word).where(models.Word.id == progress_data.word_id)
    )
    word = word_result.scalar_one_or_none()

    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )

    # 2. 查重 - 检查是否已有学习记录
    stmt = select(models.UserWordProgress).where(
        models.UserWordProgress.user_id == current_user.id,
        models.UserWordProgress.word_id == progress_data.word_id
    )
    result = await db.execute(stmt)
    existing_record = result.scalar_one_or_none()

    if existing_record:
        return existing_record

    # 3. 创建新的学习记录
    new_progress = models.UserWordProgress(
        user_id=current_user.id,
        word_id=progress_data.word_id,
        proficiency=0,
        next_review_at=datetime.now(),
        easiness_factor=2.5,
        interval=0,
        repetitions=0
    )

    db.add(new_progress)
    await db.commit()
    await db.refresh(new_progress)

    return new_progress


@router.get("/needs-review", response_model=List[schemas.ProgressWithWord])
async def get_words_to_review(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    获取需要复习的单词列表 - 基于SM-2算法的时间安排

    Args:
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        需要复习的单词列表（带词汇详情）
    """
    now = datetime.now()
    stmt = (
        select(models.UserWordProgress)
        .options(selectinload(models.UserWordProgress.word))
        .where(
            models.UserWordProgress.user_id == current_user.id,
            models.UserWordProgress.next_review_at <= now
        )
        .order_by(models.UserWordProgress.next_review_at)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/review", response_model=schemas.ProgressOut)
async def review_word(
    review_data: schemas.ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    SM-2算法复习接口 - 用户复习单词后更新进度

    Args:
        review_data: 复习数据（包含word_id和quality评分）
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        更新后的学习进度记录

    Raises:
        HTTPException: 当word_id或quality无效时
    """
    # 1. 验证评分范围
    if not (0 <= review_data.quality <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quality must be between 0 and 5"
        )

    # 2. 查找进度记录
    stmt = select(models.UserWordProgress).where(
        models.UserWordProgress.user_id == current_user.id,
        models.UserWordProgress.word_id == review_data.word_id
    )
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    # 如果还没学过这个词，先创建一条进度记录（容错处理）
    if not progress:
        progress = models.UserWordProgress(
            user_id=current_user.id,
            word_id=review_data.word_id,
            easiness_factor=2.5,
            interval=0,
            repetitions=0
        )
        db.add(progress)

    # 3. 提取当前状态
    q = review_data.quality
    ef = progress.easiness_factor
    reps = progress.repetitions
    interval = progress.interval

    # 4. 运行 SM-2 算法
    if q < 3:
        # --- 失败分支 ---
        # 如果忘了 (0-2分)，进度重置
        reps = 0
        interval = 1
        # EF 保持不变 (原版 SM-2 只有成功才调整 EF)
    else:
        # --- 成功分支 ---
        # A. 计算新的 EF
        # 公式：EF' = EF + (0.1 - (5-q) * (0.08 + (5-q)*0.02))
        new_ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        if new_ef < 1.3:
            new_ef = 1.3  # 设定下限，防止死循环
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

    # 5. 更新数据库对象
    progress.easiness_factor = ef
    progress.repetitions = reps
    progress.interval = interval
    progress.last_reviewed_at = datetime.now()
    progress.next_review_at = datetime.now() + timedelta(days=interval)

    # 6. 更新熟练度 (仅作 UI 展示，非算法核心)
    # 简单逻辑：连续对的次数越多，熟练度越高，封顶 100
    progress.proficiency = min(reps * 20, 100)

    # 7. 提交事务
    await db.commit()
    await db.refresh(progress)

    return progress


@router.get("/progress", response_model=List[schemas.ProgressWithWord])
async def get_all_progress(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    获取用户所有学习进度记录

    Args:
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        用户的全部学习进度记录（带词汇详情）
    """
    stmt = (
        select(models.UserWordProgress)
        .options(selectinload(models.UserWordProgress.word))
        .where(models.UserWordProgress.user_id == current_user.id)
        .order_by(models.UserWordProgress.last_reviewed_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/progress/stats")
async def get_learning_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    获取用户学习统计信息

    Args:
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        学习统计数据
    """
    # 1. 总学习单词数
    total_stmt = select(models.UserWordProgress).where(
        models.UserWordProgress.user_id == current_user.id
    )
    total_result = await db.execute(total_stmt)
    total_words = len(total_result.scalars().all())

    # 2. 需要复习的单词数
    now = datetime.now()
    review_stmt = select(models.UserWordProgress).where(
        models.UserWordProgress.user_id == current_user.id,
        models.UserWordProgress.next_review_at <= now
    )
    review_result = await db.execute(review_stmt)
    review_count = len(review_result.scalars().all())

    # 3. 已掌握的单词数（proficiency >= 80）
    mastered_stmt = select(models.UserWordProgress).where(
        models.UserWordProgress.user_id == current_user.id,
        models.UserWordProgress.proficiency >= 80
    )
    mastered_result = await db.execute(mastered_stmt)
    mastered_count = len(mastered_result.scalars().all())

    # 4. 平均熟练度
    avg_stmt = select(models.UserWordProgress.proficiency).where(
        models.UserWordProgress.user_id == current_user.id
    )
    avg_result = await db.execute(avg_stmt)
    avg_proficiencies = [row[0] for row in avg_result.fetchall()]
    avg_proficiency = sum(avg_proficiencies) / len(avg_proficiencies) if avg_proficiencies else 0

    return {
        "total_words": total_words,
        "review_count": review_count,
        "mastered_count": mastered_count,
        "avg_proficiency": round(avg_proficiency, 1)
    }


@router.delete("/progress/{word_id}")
async def delete_word_progress(
    word_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    删除特定单词的学习进度记录

    Args:
        word_id: 单词ID
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        删除成功消息

    Raises:
        HTTPException: 当记录不存在时
    """
    stmt = select(models.UserWordProgress).where(
        models.UserWordProgress.user_id == current_user.id,
        models.UserWordProgress.word_id == word_id
    )
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress record not found"
        )

    await db.delete(progress)
    await db.commit()

    return {"message": "Progress record deleted successfully"}