"""
词汇书管理接口测试
测试词汇书相关的API基础功能
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unauthorized_books_access(client: AsyncClient):
    """测试未授权访问词汇书接口"""
    response = await client.get("/api/v1/books/")
    assert response.status_code == 401

    response = await client.get("/api/v1/books/1")
    assert response.status_code == 401

    response = await client.get("/api/v1/books/1/words")
    assert response.status_code == 401

    response = await client.get("/api/v1/books/1/words/search/test")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_books(client: AsyncClient, test_user):
    """测试获取词汇书列表"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/books/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # 测试书中应该有测试数据
    assert len(data) >= 1
    assert "title" in data[0] if data else True


@pytest.mark.asyncio
async def test_get_book_detail(client: AsyncClient, test_user):
    """测试获取特定词汇书详情"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/books/1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "code" in data


@pytest.mark.asyncio
async def test_get_book_words(client: AsyncClient, test_user):
    """测试获取词汇书单词列表"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/books/1/words", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # 应该有测试单词
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_search_words(client: AsyncClient, test_user):
    """测试搜索单词"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/books/1/words/search/test", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_nonexistent_book(client: AsyncClient, test_user):
    """测试访问不存在的词汇书"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/books/999", headers=headers)
    assert response.status_code == 404

    response = await client.get("/api/v1/books/999/words", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_books_word_count(client: AsyncClient, test_user):
    """测试获取词汇书单词总数"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/books/1/words/count", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "book_id" in data
    assert "total_words" in data
    assert isinstance(data["total_words"], int)


@pytest.mark.asyncio
async def test_books_stats(client: AsyncClient, test_user):
    """测试获取词汇书学习统计"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/books/1/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "book_id" in data
    assert "book_title" in data
    assert "total_words_in_book" in data
    assert "learned_words" in data