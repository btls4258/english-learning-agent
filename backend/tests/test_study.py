# backend/tests/test_study.py
import pytest
from app import schemas

# 标记这是一个异步测试
@pytest.mark.asyncio
async def test_full_learning_flow(client, test_user):
    """
    测试全流程：创建进度 -> 复习(5分) -> 复习(4分) -> 复习(0分)
    """
    token = test_user["token"]
    word_id = test_user["word_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # -------------------------------------------
    # 1. 模拟：开始学习单词 (POST /study/progress)
    # -------------------------------------------
    resp = await client.post(
        "/study/progress",
        json={"word_id": word_id},
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["word_id"] == word_id
    assert data["proficiency"] == 0
    assert data["easiness_factor"] == 2.5 # 初始值检查
    
    print("\n[Pass] 进度创建成功")

    # -------------------------------------------
    # 2. 模拟：第一次复习，打 5 分 (POST /study/review)
    # -------------------------------------------
    resp = await client.post(
        "/study/review",
        json={"word_id": word_id, "quality": 5},
        headers=headers
    )
    data = resp.json()
    
    # 验证 SM-2 逻辑 (第一次对 -> 间隔1天)
    assert data["repetitions"] == 1
    assert data["interval"] == 1
    assert data["easiness_factor"] > 2.5 # 应该变大
    
    print("[Pass] 第一次复习逻辑正确 (Interval=1)")

    # -------------------------------------------
    # 3. 模拟：第二次复习，打 4 分
    # -------------------------------------------
    resp = await client.post(
        "/study/review",
        json={"word_id": word_id, "quality": 4},
        headers=headers
    )
    data = resp.json()
    
    # 验证 SM-2 逻辑 (第二次对 -> 间隔6天)
    assert data["repetitions"] == 2
    assert data["interval"] == 6
    
    print("[Pass] 第二次复习逻辑正确 (Interval=6)")

    # -------------------------------------------
    # 4. 模拟：第三次复习，忘了 (0分)
    # -------------------------------------------
    resp = await client.post(
        "/study/review",
        json={"word_id": word_id, "quality": 0},
        headers=headers
    )
    data = resp.json()
    
    # 验证 SM-2 逻辑 (失败 -> 重置)
    assert data["repetitions"] == 0
    assert data["interval"] == 1
    
    print("[Pass] 遗忘逻辑正确 (Interval重置为1)")