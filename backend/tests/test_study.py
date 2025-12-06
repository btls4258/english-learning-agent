# backend/tests/test_study.py
import pytest
from httpx import AsyncClient
from app import schemas

@pytest.mark.asyncio
async def test_full_learning_flow(client, test_user):
    """测试完整学习流程：创建进度 -> 复习(5分) -> 复习(4分) -> 复习(0分)"""
    token = test_user["token"]
    word_id = test_user["word_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 创建学习进度
    resp = await client.post("/api/v1/study/progress", json={"word_id": word_id}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["word_id"] == word_id
    assert data["proficiency"] == 0
    assert data["easiness_factor"] == 2.5

    # 2. 第一次复习（5分）
    resp = await client.post("/api/v1/study/review", json={"word_id": word_id, "quality": 5}, headers=headers)
    data = resp.json()
    assert data["repetitions"] == 1
    assert data["interval"] == 1
    assert data["easiness_factor"] > 2.5

    # 3. 第二次复习（4分）
    resp = await client.post("/api/v1/study/review", json={"word_id": word_id, "quality": 4}, headers=headers)
    data = resp.json()
    assert data["repetitions"] == 2
    assert data["interval"] == 6

    # 4. 第三次复习（0分，忘记）
    resp = await client.post("/api/v1/study/review", json={"word_id": word_id, "quality": 0}, headers=headers)
    data = resp.json()
    assert data["repetitions"] == 0
    assert data["interval"] == 1


@pytest.mark.asyncio
async def test_sm2_algorithm_cases(client, test_user):
    """测试SM-2算法的不同情况"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 测试第一次复习的情况（repetitions=1, interval=1）
    first_review_cases = [
        0, 1, 2, 3, 4, 5  # 所有可能的质量评分
    ]

    for i, quality in enumerate(first_review_cases):
        # 为每个测试创建不同的单词
        word_id = test_user["word_id"] + i
        if word_id <= test_user["word_id"] + 10:  # 确保不超出测试数据范围
            # 创建新进度
            await client.post("/api/v1/study/progress", json={"word_id": word_id}, headers=headers)

            # 进行复习
            resp = await client.post("/api/v1/study/review", json={"word_id": word_id, "quality": quality}, headers=headers)
            data = resp.json()

            if quality < 3:
                # 失败情况：重置为0
                assert data["repetitions"] == 0
                assert data["interval"] == 1
            else:
                # 成功情况：repetitions=1, interval=1
                assert data["repetitions"] == 1
                assert data["interval"] == 1


@pytest.mark.asyncio
async def test_study_progress_list(client: AsyncClient, test_user):
    """测试获取学习进度列表"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/study/progress", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_study_progress_stats(client: AsyncClient, test_user):
    """测试获取学习进度统计"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/study/progress/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # 可能包含的统计字段
    possible_fields = ["total_words", "learned_words", "mastered_words", "review_count"]
    assert any(field in data for field in possible_fields)


@pytest.mark.asyncio
async def test_delete_progress(client: AsyncClient, test_user):
    """测试删除学习进度"""
    token = test_user["token"]
    word_id = test_user["word_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 先创建学习进度
    await client.post("/api/v1/study/progress", json={"word_id": word_id}, headers=headers)

    # 然后删除它
    response = await client.delete(f"/api/v1/study/progress/{word_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data