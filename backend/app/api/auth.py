# backend/app/api/auth.py
"""
认证相关的API路由 - 用户注册、登录、JWT管理
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user
from app.security import (
    verify_password,
    create_access_token,
    get_password_hash,
    SECRET_KEY,
    ALGORITHM
)
from jose import JWTError, jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])

# 认证相关异常
class AuthenticationError(Exception):
    pass


@router.post("/register", response_model=schemas.UserOut)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    注册新用户

    Args:
        user: 用户创建数据
        db: 数据库会话

    Returns:
        创建的用户信息

    Raises:
        HTTPException: 当邮箱已注册时
    """
    # 1. 查询邮箱是否存在
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    db_user = result.scalar_one_or_none()

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 2. 准备数据库模型对象
    new_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )

    # 3. 添加到会话并提交
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=schemas.Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录接口 (获取 Token)

    Args:
        form_data: OAuth2PasswordRequestForm (username字段实际存储email)
        db: 数据库会话

    Returns:
        JWT token信息

    Raises:
        HTTPException: 当认证失败时
    """
    try:
        # 1. 尝试在数据库中查找用户 (按邮箱查找)
        stmt = select(models.User).where(models.User.email == form_data.username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        # 2. 验证用户是否存在，以及密码是否正确
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. 登录成功，生成 Token
        access_token_expires = timedelta(minutes=30)  # 30分钟有效期
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )

        # 4. 返回 Token 给前端
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException:
        # 重新抛出HTTP异常（如401）
        raise
    except Exception as e:
        # 捕获其他异常，返回详细错误信息用于调试
        import traceback
        error_detail = f"登录处理失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get("/me", response_model=schemas.UserOut)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
):
    """
    获取当前登录用户信息

    Args:
        current_user: 当前认证用户

    Returns:
        用户信息
    """
    return current_user


@router.post("/logout")
async def logout_user():
    """
    用户登出接口

    Note: JWT是无状态的，登出主要在客户端删除token
    后端接口主要用于记录登出事件（如果需要）

    Returns:
        登出成功消息
    """
    return {"message": "Logout successful. Please delete the token on client side."}


@router.get("/token/validate")
async def validate_token(
    current_user: models.User = Depends(get_current_user)
):
    """
    验证当前token是否有效

    Args:
        current_user: 当前认证用户

    Returns:
        token验证结果
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }