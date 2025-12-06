# backend/app/api/books.py
"""
词汇书相关的API路由 - 词汇书管理、单词查询
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=List[dict])
async def get_books(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    获取所有词汇书列表

    Args:
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        词汇书列表
    """
    stmt = select(models.Book.id, models.Book.title, models.Book.code, models.Book.description).order_by(models.Book.id)
    result = await db.execute(stmt)
    books = result.all()

    # 转换为字典列表，避免递归
    return [
        {
            "id": book.id,
            "title": book.title,
            "code": book.code,
            "description": book.description
        }
        for book in books
    ]


@router.get("/{book_id}", response_model=dict)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    获取特定词汇书详情

    Args:
        book_id: 词汇书ID
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        词汇书详情

    Raises:
        HTTPException: 当词汇书不存在时
    """
    stmt = select(models.Book.id, models.Book.title, models.Book.code, models.Book.description).where(models.Book.id == book_id)
    result = await db.execute(stmt)
    book = result.first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return {
        "id": book.id,
        "title": book.title,
        "code": book.code,
        "description": book.description
    }


@router.get("/{book_id}/words", response_model=List[dict])
async def get_book_words(
    book_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    获取指定词汇书的单词列表（支持分页）

    Args:
        book_id: 词汇书ID
        skip: 跳过的单词数量（用于分页）
        limit: 返回的单词数量限制
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        单词列表

    Raises:
        HTTPException: 当词汇书不存在时
    """
    # 先验证词汇书是否存在
    book_stmt = select(models.Book).where(models.Book.id == book_id)
    book_result = await db.execute(book_stmt)
    book = book_result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # 查询单词（支持分页）
    word_stmt = (
        select(
            models.Word.id,
            models.Word.spelling,
            models.Word.phonetic,
            models.Word.meaning,
            models.Word.book_id
        )
        .where(models.Word.book_id == book_id)
        .offset(skip)
        .limit(limit)
        .order_by(models.Word.id)
    )
    result = await db.execute(word_stmt)
    words = result.all()

    # 转换为字典列表
    return [
        {
            "id": word.id,
            "spelling": word.spelling,
            "phonetic": word.phonetic,
            "meaning": word.meaning,
            "book_id": word.book_id
        }
        for word in words
    ]


@router.get("/{book_id}/words/count")
async def get_book_words_count(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    获取指定词汇书的单词总数

    Args:
        book_id: 词汇书ID
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        单词总数

    Raises:
        HTTPException: 当词汇书不存在时
    """
    # 先验证词汇书是否存在
    book_stmt = select(models.Book).where(models.Book.id == book_id)
    book_result = await db.execute(book_stmt)
    book = book_result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # 查询单词总数
    count_stmt = select(models.Word).where(models.Word.book_id == book_id)
    count_result = await db.execute(count_stmt)
    total_count = len(count_result.scalars().all())

    return {"book_id": book_id, "total_words": total_count}


@router.get("/{book_id}/words/search/{search_term}", response_model=List[dict])
async def search_words_in_book(
    book_id: int,
    search_term: str,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    在指定词汇书中搜索单词

    Args:
        book_id: 词汇书ID
        search_term: 搜索关键词
        skip: 跳过的单词数量
        limit: 返回的单词数量限制
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        匹配的单词列表

    Raises:
        HTTPException: 当词汇书不存在时
    """
    # 先验证词汇书是否存在
    book_stmt = select(models.Book).where(models.Book.id == book_id)
    book_result = await db.execute(book_stmt)
    book = book_result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # 搜索单词（英文单词或中文释义）
    search_pattern = f"%{search_term}%"
    word_stmt = (
        select(
            models.Word.id,
            models.Word.spelling,
            models.Word.phonetic,
            models.Word.meaning,
            models.Word.book_id
        )
        .where(
            models.Word.book_id == book_id,
            (models.Word.spelling.ilike(search_pattern) |
             models.Word.meaning.ilike(search_pattern))
        )
        .offset(skip)
        .limit(limit)
        .order_by(models.Word.id)
    )
    result = await db.execute(word_stmt)
    words = result.all()

    # 转换为字典列表
    return [
        {
            "id": word.id,
            "spelling": word.spelling,
            "phonetic": word.phonetic,
            "meaning": word.meaning,
            "book_id": word.book_id
        }
        for word in words
    ]


@router.get("/{book_id}/stats")
async def get_book_statistics(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    获取用户在特定词汇书中的学习统计

    Args:
        book_id: 词汇书ID
        db: 数据库会话
        current_user: 当前认证用户

    Returns:
        学习统计数据

    Raises:
        HTTPException: 当词汇书不存在时
    """
    # 验证词汇书是否存在
    book_stmt = select(models.Book).where(models.Book.id == book_id)
    book_result = await db.execute(book_stmt)
    book = book_result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # 获取用户在该词汇书中的学习进度
    progress_stmt = (
        select(models.UserWordProgress)
        .join(models.Word, models.UserWordProgress.word_id == models.Word.id)
        .where(
            models.UserWordProgress.user_id == current_user.id,
            models.Word.book_id == book_id
        )
    )
    progress_result = await db.execute(progress_stmt)
    user_progress = progress_result.scalars().all()

    # 获取词汇书总单词数（只查询一次）
    total_words_stmt = select(func.count(models.Word.id)).where(models.Word.book_id == book_id)
    total_words_result = await db.execute(total_words_stmt)
    total_words_in_book = total_words_result.scalar()

    # 统计信息
    total_progress = len(user_progress)
    mastered_count = sum(1 for p in user_progress if p.proficiency >= 80)
    review_count = sum(1 for p in user_progress if p.next_review_at <= datetime.now())

    return {
        "book_id": book_id,
        "book_title": book.title,
        "total_words_in_book": total_words_in_book,
        "learned_words": total_progress,
        "mastered_words": mastered_count,
        "words_need_review": review_count,
        "progress_percentage": round((total_progress / total_words_in_book) * 100, 1) if total_words_in_book > 0 else 0.0
    }