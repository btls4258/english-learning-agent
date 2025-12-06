"""
英语学习Agent核心功能测试
专注测试Agent的基础功能，避免过度复杂化
"""
import pytest
from unittest.mock import Mock, patch
from app.agents.english_learning_agent import EnglishLearningAgent, agent_manager


@pytest.mark.asyncio
async def test_agent_initialization():
    """测试Agent初始化"""
    with patch('app.agents.english_learning_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_get_llm.return_value = mock_llm

        user_context = {"level": "beginner", "goals": ["vocabulary"]}
        agent = EnglishLearningAgent(provider="deepseek", user_context=user_context)

        assert agent.provider == "deepseek"
        assert agent.user_context["level"] == "beginner"
        assert len(agent.tools) == 9  # 9个学习工具


def test_agent_manager():
    """测试Agent管理器基本功能"""
    # 创建Agent
    agent1 = agent_manager.get_agent(user_id=1, provider="deepseek")
    agent2 = agent_manager.get_agent(user_id=1)  # 复用

    # 测试复用
    assert agent1 is agent2

    # 清理
    agent_manager.clear_all_agents()
    assert len(agent_manager.get_all_agents_info()) == 0


def test_user_context():
    """测试用户上下文功能"""
    agent = EnglishLearningAgent(provider="deepseek", user_context={"level": "intermediate"})

    context = agent.get_user_context()
    assert context["level"] == "intermediate"

    # 更新上下文
    agent.update_user_context(level="advanced")
    updated_context = agent.get_user_context()
    assert updated_context["level"] == "advanced"


def test_history_management():
    """测试对话历史管理"""
    agent = EnglishLearningAgent(provider="deepseek")

    # 初始历史为空
    assert len(agent.get_history()) == 0

    # 清空历史（应该不报错）
    agent.clear_history()
    assert len(agent.get_history()) == 0