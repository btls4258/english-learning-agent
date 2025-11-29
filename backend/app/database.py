#/home/btls/english-learning-agent/backend/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# 1. 加载 .env 里的环境变量
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. 创建数据库引擎 (Engine)
# echo=True 表示会在控制台打印出执行的 SQL 语句，方便调试，上线后可以关掉
engine = create_async_engine(DATABASE_URL, echo=True)

# 3. 创建会话工厂 (SessionLocal)
# 每次请求数据库时，我们都从这里拿一个 Session
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 4. 创建基类 (Base)
# 以后我们定义数据库表（Model）时，都要继承这个 Base
Base = declarative_base()

# 5. 获取数据库会话的依赖函数 (Dependency)
# 这是给 FastAPI 接口用的，保证请求结束时自动关闭连接
async def get_db():
    async with SessionLocal() as session:
        yield session