# backend/app/dependencies.py
"""
FastAPI依赖函数
用于处理认证、数据库等依赖注入
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from app.database import get_db
from app import models
from app.security import SECRET_KEY, ALGORITHM

# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> models.User:
    """
    智能门禁函数：
    1. 自动从请求头 Authorization: Bearer <token> 中提取 token
    2. 解析 token 获取邮箱
    3. 查数据库返回 User 对象
    """
    # 定义一个"认证失败"的异常，后面如果出错就抛出这个
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # A. 解密 Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # B. 取出 Token 里的身份标识 (我们在登录时把 email 放进了 sub 字段)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        # 如果 Token 被篡改、过期或格式不对，会报错
        raise credentials_exception

    # C. 去数据库核实这个人是否还存在
    stmt = select(models.User).where(models.User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    # D. 返回完整的用户对象 (包含 id, username, email 等)
    return user

