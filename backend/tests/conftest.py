# backend/tests/conftest.py
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.security import create_access_token, get_password_hash
from app.models import User, Book, Word
import os

# 使用内存数据库进行快速测试
# 注意：必须安装 aiosqlite (pip install aiosqlite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 创建测试专用的引擎
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """
    创建事件循环。
    pytest-asyncio 默认现在的策略是每个 test 一个 loop，
    但为了配合 session 级别的 fixture，我们需要手动定义这个。
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    """
    每次测试函数运行时，创建一个新的数据库会话。
    测试开始前建表，测试结束后删表，保证环境干净。
    """
    # 1. 建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. 创建会话
    async with TestingSessionLocal() as session:
        yield session
        # 测试结束，回滚事务
        await session.rollback()

    # 3. 删表 (清理环境)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db_session):
    """
    创建一个虚拟的客户端 (类似 Postman)，用于发请求。
    这里会覆盖 main.py 里的 get_db 依赖，让它使用我们的测试数据库。
    """
    # 定义覆盖函数
    async def override_get_db():
        yield db_session

    # 应用覆盖
    app.dependency_overrides[get_db] = override_get_db
    
    # 【修复关键点】：使用 ASGITransport 来挂载 FastAPI app
    transport = ASGITransport(app=app)
    
    # 创建异步客户端
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    
    # 清理覆盖
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def test_user(db_session):
    """
    预先在数据库里插入一个测试用户、一本测试书、一个测试单词。
    并返回该用户的 Token，方便测试用例直接调用。
    """
    # 1. 创建用户
    user = User(
        email="test@example.com", 
        username="TestUser", 
        hashed_password=get_password_hash("testpass")
    )
    db_session.add(user)
    
    # 2. 创建基础数据 (书 + 词)
    book = Book(title="Test Book", code="test_book")
    word = Word(spelling="test", meaning="测试", book=book)
    # SQLAlchemy 会自动处理 book 和 word 的关联，只要 add 进去即可
    db_session.add(book)
    db_session.add(word)

    # 提交保存
    await db_session.commit()
    await db_session.refresh(user)
    
    # 3. 生成 Token
    token = create_access_token(data={"sub": user.email})
    
    # 返回打包好的数据
    return {"user": user, "token": token, "word_id": word.id}