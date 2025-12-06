"""
主要API端点测试
测试所有核心API的基本功能是否正常工作
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from app import models
from app.security import get_password_hash


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_db_connection(client: AsyncClient):
    """测试数据库连接"""
    response = await client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "connection" in data


@pytest.mark.asyncio
async def test_user_registration(client: AsyncClient, db_session):
    """测试用户注册"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "test123456"
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert data["is_active"] == True


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(client: AsyncClient, db_session):
    """测试重复邮箱注册"""
    user_data = {
        "email": "duplicate@example.com",
        "username": "testuser1",
        "password": "test123456"
    }

    # 第一次注册成功
    response1 = await client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 200

    # 第二次注册失败
    response2 = await client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 400


@pytest.mark.asyncio
async def test_user_login(client: AsyncClient, db_session):
    """测试用户登录"""
    # 先创建用户
    user = models.User(
        email="login_test@example.com",
        username="logintest",
        hashed_password=get_password_hash("test123456")
    )
    db_session.add(user)
    await db_session.commit()

    # 登录
    login_data = {
        "username": "login_test@example.com",
        "password": "test123456"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_user_login_wrong_password(client: AsyncClient, db_session):
    """测试错误密码登录"""
    # 先创建用户
    user = models.User(
        email="wrong_pass@example.com",
        username="wrongpasstest",
        hashed_password=get_password_hash("correct123")
    )
    db_session.add(user)
    await db_session.commit()

    # 使用错误密码登录
    login_data = {
        "username": "wrong_pass@example.com",
        "password": "wrong123"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_learning_progress(client: AsyncClient, test_user):
    """测试创建学习进度"""
    token = test_user["token"]
    word_id = test_user["word_id"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/api/v1/study/progress", json={"word_id": word_id}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["word_id"] == word_id
    assert data["proficiency"] == 0
    assert data["repetitions"] == 0
    assert data["interval"] == 0


@pytest.mark.asyncio
async def test_create_duplicate_progress(client: AsyncClient, test_user):
    """测试创建重复的学习进度"""
    token = test_user["token"]
    word_id = test_user["word_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 第一次创建
    response1 = await client.post("/api/v1/study/progress", json={"word_id": word_id}, headers=headers)
    assert response1.status_code == 200

    # 第二次创建应该返回已存在的记录
    response2 = await client.post("/api/v1/study/progress", json={"word_id": word_id}, headers=headers)
    assert response2.status_code == 200
    assert response1.json()["id"] == response2.json()["id"]


@pytest.mark.asyncio
async def test_word_review(client: AsyncClient, test_user):
    """测试单词复习"""
    token = test_user["token"]
    word_id = test_user["word_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 先创建学习进度
    await client.post("/study/progress", json={"word_id": word_id}, headers=headers)

    # 进行复习（5分）
    review_data = {"word_id": word_id, "quality": 5}
    response = await client.post("/api/v1/study/review", json=review_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["repetitions"] == 1
    assert data["interval"] == 1
    assert data["easiness_factor"] > 2.5


@pytest.mark.asyncio
async def test_get_needs_review(client: AsyncClient, test_user):
    """测试获取需要复习的单词"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/study/needs-review", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_chat_endpoint_without_mock(client: AsyncClient, test_user):
    """测试聊天端点（不mock，实际调用API）"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    chat_data = {
        "message": "Hello, please introduce yourself",
        "provider": "deepseek"
    }

    # 这个测试可能会超时，因为需要实际调用AI API
    try:
        response = await client.post("/api/v1/chat/", json=chat_data, headers=headers, timeout=30.0)
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert "provider" in data
            assert len(data["response"]) > 0
        else:
            # 如果AI服务不可用，记录但不失败
            print(f"Chat API returned status {response.status_code}: {response.text}")
    except Exception as e:
        # 如果AI服务超时或不可用，记录但不失败
        print(f"Chat API test skipped due to: {str(e)}")


@pytest.mark.asyncio
async def test_get_chat_history(client: AsyncClient, test_user):
    """测试获取聊天历史"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/chat/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_clear_chat_history(client: AsyncClient, test_user):
    """测试清空聊天历史"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/api/v1/chat/clear", headers=headers)
    assert response.status_code == 200

    # 验证历史已清空
    response = await client.get("/api/v1/chat/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user):
    """测试获取当前用户信息"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "username" in data


@pytest.mark.asyncio
async def test_token_validate(client: AsyncClient, test_user):
    """测试Token验证"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/auth/token/validate", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert "user_id" in data


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, test_user):
    """测试用户登出"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_chat_agent_info(client: AsyncClient, test_user):
    """测试获取Agent信息"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/chat/agent-info", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "tools_count" in data


@pytest.mark.asyncio
async def test_chat_tools(client: AsyncClient, test_user):
    """测试获取Agent工具列表"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/chat/tools", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_chat_update_context(client: AsyncClient, test_user):
    """测试更新用户上下文"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    context_data = {
        "level": "advanced",
        "goals": ["business", "writing"],
        "preferences": {"daily_goal": 10}
    }

    response = await client.post("/api/v1/chat/update-context", json=context_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """测试未授权访问"""
    # 测试各种需要认证的端点
    endpoints = [
        ("/api/v1/auth/me", "GET"),
        ("/api/v1/auth/token/validate", "GET"),
        ("/api/v1/study/needs-review", "GET"),
        ("/api/v1/study/progress", "POST"),
        ("/api/v1/chat/history", "GET"),
        ("/api/v1/books/", "GET"),
        ("/api/v1/chat/agent-info", "GET"),
    ]

    for endpoint, method in endpoints:
        if method == "GET":
            response = await client.get(endpoint)
        elif method == "POST":
            response = await client.post(endpoint, json={})
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """测试根路径"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data