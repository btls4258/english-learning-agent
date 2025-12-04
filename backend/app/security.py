from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# 1. 配置密码加密上下文
# schemes=["bcrypt"] 表示我们将使用 bcrypt 算法来加密密码
# deprecated="auto" 表示如果将来 bcrypt 过时了，它会自动处理旧密码
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. 获取配置
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# 验证必需配置
if not SECRET_KEY:
    raise ValueError("SECRET_KEY环境变量未设置，请在.env文件中配置")

# --- 核心函数 1：密码处理 ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确。
    plain_password: 用户输入的明文密码 (如 "123456")
    hashed_password: 数据库里存的密文 (如 "$2b$12$...")
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    将明文密码加密成哈希值。
    """
    return pwd_context.hash(password)

# --- 核心函数 2：Token 生成 ---

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    生成 JWT Token。
    data: 要加密到 Token 里的数据 (比如 user_id, sub/username)
    expires_delta: 过期时间，如果不传则默认使用配置的时间
    """
    to_encode = data.copy()
    
    # 计算过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 把过期时间写进 Token 数据里
    to_encode.update({"exp": expire})
    
    # 生成加密字符串
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt