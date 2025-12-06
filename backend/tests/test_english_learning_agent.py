# backend/tests/test_english_learning_agent.py
"""
英语学习Agent功能测试
测试新的LangChain v1.0架构的Agent实现
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.agents.english_learning_agent import EnglishLearningAgent, AgentManager
from app.agents.tools.learning_tools import (
    search_dictionary,
    create_vocabulary_exercise,
    get_grammar_explanation
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


@pytest.mark.asyncio
async def test_english_learning_agent_initialization():
    """测试英语学习Agent初始化"""
    with patch('app.agents.english_learning_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_get_llm.return_value = mock_llm

        user_context = {"level": "beginner", "goals": ["vocabulary", "conversation"]}
        agent = EnglishLearningAgent(provider="deepseek", user_context=user_context)

        assert agent.llm == mock_llm
        assert agent.provider == "deepseek"
        assert agent.user_context["level"] == "beginner"
        assert "vocabulary" in agent.user_context["goals"]
        assert len(agent.tools) == 9  # 9个学习工具


@pytest.mark.asyncio
async def test_agent_with_system_prompt():
    """测试Agent的系统提示词构建"""
    with patch('app.agents.english_learning_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "glm4"
        mock_get_llm.return_value = mock_llm

        user_context = {"level": "advanced", "goals": ["business", "writing"]}
        agent = EnglishLearningAgent(provider="glm4", user_context=user_context)

        system_prompt = agent.system_prompt

        assert "英语学习AI助教" in system_prompt
        assert "advanced" in system_prompt
        assert "business" in system_prompt
        assert "writing" in system_prompt


@pytest.mark.asyncio
async def test_agent_chat_single_message():
    """测试Agent单轮对话"""
    with patch('app.agents.english_learning_agent.get_llm') as mock_get_llm:
        # 模拟Agent响应
        mock_agent_response = {
            "messages": [
                {"role": "assistant", "content": "Hello! I'm your English learning assistant Emma."}
            ]
        }

        # 设置mock函数的返回值 - 现在需要mock agent.invoke()
        mock_agent = Mock()
        mock_agent.invoke = Mock(return_value=mock_agent_response)

        mock_get_llm.return_value = Mock()
        mock_get_llm.return_value._llm_type = "deepseek"

        # 创建Agent并替换为mock agent
        agent = EnglishLearningAgent(provider="deepseek")
        agent.agent = mock_agent

        response = agent.chat("Hello")

        assert response == "Hello! I'm your English learning assistant Emma."
        assert len(agent.conversation_history) == 2


@pytest.mark.asyncio
async def test_agent_chat_multi_turn_conversation():
    """测试Agent多轮对话"""
    with patch('app.agents.english_learning_agent.get_llm') as mock_get_llm:
        # 模拟多次对话响应
        mock_response1 = {
            "messages": [
                {"role": "assistant", "content": "Hi there! How can I help you today?"}
            ]
        }
        mock_response2 = {
            "messages": [
                {"role": "assistant", "content": "You asked about the word 'accomplish'. It means to complete or achieve something successfully."}
            ]
        }

        # 设置mock函数的返回值序列 - 现在需要mock agent.invoke()
        mock_agent = Mock()
        mock_agent.invoke = Mock(side_effect=[mock_response1, mock_response2])

        mock_get_llm.return_value = Mock()
        mock_get_llm.return_value._llm_type = "deepseek"

        # 创建Agent并替换为mock agent
        agent = EnglishLearningAgent(provider="deepseek")
        agent.agent = mock_agent

        # 第一轮对话
        response1 = agent.chat("What does 'accomplish' mean?")
        assert response1 == "Hi there! How can I help you today?"
        assert len(agent.conversation_history) == 2

        # 第二轮对话
        response2 = agent.chat("Can you explain it again?")
        assert response2 == "You asked about the word 'accomplish'. It means to complete or achieve something successfully."
        assert len(agent.conversation_history) == 4

        assert mock_agent.invoke.call_count == 2


@pytest.mark.asyncio
async def test_agent_clear_history():
    """测试清空对话历史"""
    with patch('app.agents.english_learning_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"

        mock_response = {
            "messages": [AIMessage(content="Response")]
        }
        mock_agent_executor = Mock()
        mock_agent_executor.invoke = Mock(return_value=mock_response)

        agent = EnglishLearningAgent(provider="deepseek")
        agent.agent = mock_agent_executor

        # 添加一些对话历史
        agent.chat("Hello")
        assert len(agent.conversation_history) == 2

        # 清空历史
        agent.clear_history()
        assert len(agent.conversation_history) == 0


@pytest.mark.asyncio
async def test_agent_update_user_context():
    """测试更新用户上下文"""
    with patch('app.agents.english_learning_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_get_llm.return_value = mock_llm

        agent = EnglishLearningAgent(provider="deepseek")
        original_context = agent.user_context.copy()

        # 更新上下文
        agent.update_user_context(level="intermediate", new_goal="grammar")
        updated_context = agent.user_context

        assert updated_context != original_context
        assert updated_context["level"] == "intermediate"
        assert updated_context["new_goal"] == "grammar"


@pytest.mark.asyncio
async def test_agent_manager():
    """测试Agent管理器"""
    with patch('app.agents.english_learning_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_get_llm.return_value = mock_llm

        manager = AgentManager()

        # 创建新的Agent实例
        agent1 = manager.get_agent(user_id=1, provider="deepseek")
        assert isinstance(agent1, EnglishLearningAgent)
        assert manager.get_all_agents_info()[1]["provider"] == "deepseek"

        # 获取已存在的Agent实例
        agent2 = manager.get_agent(user_id=1)
        assert agent1 is agent2  # 应该是同一个实例

        # 创建不同用户的Agent
        agent3 = manager.get_agent(user_id=2, provider="glm4")
        assert agent3 is not agent1
        assert len(manager.get_all_agents_info()) == 2

        # 移除Agent
        manager.remove_agent(user_id=1)
        assert len(manager.get_all_agents_info()) == 1

        # 清空所有Agent
        manager.clear_all_agents()
        assert len(manager.get_all_agents_info()) == 0


@pytest.mark.asyncio
async def test_search_dictionary_tool():
    """测试字典搜索工具"""
    result = search_dictionary.invoke({"word": "hello"})
    assert "hello" in result.lower()
    assert "音标" in result or "phonetic" in result.lower()
    assert "定义" in result or "definition" in result.lower()

    # 测试不存在的单词
    result = search_dictionary.invoke({"word": "unknownword123"})
    assert "未找到" in result or "not found" in result.lower()


@pytest.mark.asyncio
async def test_vocabulary_exercise_tool():
    """测试词汇练习工具"""
    result = create_vocabulary_exercise.run("animals", "beginner")
    assert "animals" in result.lower()
    assert "练习" in result
    assert "问题" in result

    # 测试不存在的主题
    result = create_vocabulary_exercise.run("unknown_topic")
    assert "unknown_topic" in result
    assert "animals" in result or "food" in result


@pytest.mark.asyncio
async def test_grammar_explanation_tool():
    """测试语法解释工具"""
    result = get_grammar_explanation.run("present tense")
    assert "present tense" in result.lower()
    assert "规则" in result
    assert "例句" in result

    # 测试不存在的语法点
    result = get_grammar_explanation.run("unknown_grammar")
    assert "unknown_grammar" in result.lower()


@pytest.mark.asyncio
async def test_agent_with_database_context():
    """测试Agent设置数据库上下文"""
    with patch('app.agents.english_learning_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_get_llm.return_value = mock_llm

        agent = EnglishLearningAgent(provider="deepseek")

        # 模拟数据库会话
        mock_db = Mock()

        # 设置学习上下文
        agent.set_learning_context(mock_db, user_id=123)

        # 验证上下文设置 - 验证agent的user_context已更新
        assert agent.user_context["user_id"] == 123


@pytest.mark.asyncio
async def test_agent_error_handling():
    """测试Agent错误处理"""
    with patch('app.agents.english_learning_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_get_llm.return_value = mock_llm

        agent = EnglishLearningAgent(provider="deepseek")

        # 模拟Agent执行失败
        mock_agent_executor = Mock()
        mock_agent_executor.invoke = Mock(side_effect=Exception("Test error"))
        agent.agent = mock_agent_executor

        response = agent.chat("Hello")

        assert "error" in response.lower() or "错误" in response
        assert len(agent.conversation_history) == 2  # 即使出错也应该保存对话


@pytest.mark.asyncio
async def test_agent_get_info():
    """测试获取Agent信息"""
    with patch('app.agents.english_learning_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_get_llm.return_value = mock_llm

        user_context = {"level": "intermediate", "goals": ["speaking"]}
        agent = EnglishLearningAgent(provider="deepseek", user_context=user_context)

        # 添加一些对话历史
        agent.chat("Hello")

        info = agent.get_agent_info()

        assert info["provider"] == "deepseek"
        assert info["tools_count"] == 9
        assert "search_dictionary" in info["tools"]
        assert info["conversation_length"] == 2
        assert info["user_context"]["level"] == "intermediate"
        assert "speaking" in info["user_context"]["goals"]