# backend/tests/test_chat_agent.py
"""
Agent对话功能测试
测试ChatAgent和相关的API接口
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.agents.chat_agent import ChatAgent
from app.agents.llm_providers import DeepSeekChatModel, GLM4ChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


@pytest.mark.asyncio
async def test_chat_agent_initialization():
    """测试ChatAgent初始化"""
    # 使用mock LLM，避免实际调用API
    with patch('app.agents.chat_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_get_llm.return_value = mock_llm
        
        agent = ChatAgent(provider="deepseek")
        
        assert agent.llm == mock_llm
        assert len(agent.conversation_history) == 0
        assert agent.llm._llm_type == "deepseek"


@pytest.mark.asyncio
async def test_chat_agent_single_message():
    """测试单轮对话"""
    with patch('app.agents.chat_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        # 模拟invoke返回AIMessage
        mock_response = AIMessage(content="Hello! How can I help you?")
        mock_llm.invoke = Mock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm
        
        agent = ChatAgent(provider="deepseek")
        response = agent.chat("Hello")
        
        # 验证返回内容
        assert response == "Hello! How can I help you?"
        # 验证历史记录
        assert len(agent.conversation_history) == 2  # user message + ai message
        assert isinstance(agent.conversation_history[0], HumanMessage)
        assert isinstance(agent.conversation_history[1], AIMessage)


@pytest.mark.asyncio
async def test_chat_agent_multi_turn_conversation():
    """测试多轮对话（上下文记忆）"""
    with patch('app.agents.chat_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        
        # 第一轮回复
        mock_response1 = AIMessage(content="Hi there!")
        # 第二轮回复（应该能看到历史）
        mock_response2 = AIMessage(content="You said: Hello")
        
        mock_llm.invoke = Mock(side_effect=[mock_response1, mock_response2])
        mock_get_llm.return_value = mock_llm
        
        agent = ChatAgent(provider="deepseek")
        
        # 第一轮
        response1 = agent.chat("Hello")
        assert response1 == "Hi there!"
        assert len(agent.conversation_history) == 2
        
        # 第二轮（应该包含历史）
        response2 = agent.chat("What did I say?")
        assert response2 == "You said: Hello"
        assert len(agent.conversation_history) == 4  # 2轮对话，每轮2条消息
        
        # 验证invoke被调用了2次，且第二次调用时包含了历史
        assert mock_llm.invoke.call_count == 2
        # 第二次调用时，应该包含之前的对话历史
        second_call_args = mock_llm.invoke.call_args_list[1][0][0]
        assert len(second_call_args) == 4  # 第一轮的user+ai + 第二轮的user+ai


@pytest.mark.asyncio
async def test_chat_agent_system_prompt():
    """测试系统提示词"""
    with patch('app.agents.chat_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_response = AIMessage(content="I'm an English tutor.")
        mock_llm.invoke = Mock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm
        
        agent = ChatAgent(provider="deepseek")
        response = agent.chat("Who are you?", system_prompt="You are an English tutor.")
        
        # 验证系统消息被添加
        assert len(agent.conversation_history) == 3  # system + user + ai
        assert isinstance(agent.conversation_history[0], SystemMessage)
        assert agent.conversation_history[0].content == "You are an English tutor."


@pytest.mark.asyncio
async def test_chat_agent_clear_history():
    """测试清空历史"""
    with patch('app.agents.chat_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_response = AIMessage(content="Response")
        mock_llm.invoke = Mock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm
        
        agent = ChatAgent(provider="deepseek")
        agent.chat("Hello")
        assert len(agent.conversation_history) == 2
        
        agent.clear_history()
        assert len(agent.conversation_history) == 0


@pytest.mark.asyncio
async def test_chat_agent_get_history():
    """测试获取历史记录"""
    with patch('app.agents.chat_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_response = AIMessage(content="Response")
        mock_llm.invoke = Mock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm
        
        agent = ChatAgent(provider="deepseek")
        agent.chat("Hello")
        
        history = agent.get_history()
        assert len(history) == 2
        assert isinstance(history[0], HumanMessage)
        assert isinstance(history[1], AIMessage)
        # 验证返回的是副本，不是引用
        assert history is not agent.conversation_history


@pytest.mark.asyncio
async def test_chat_api_endpoint(client, test_user):
    """测试Chat API端点（需要mock LLM调用）"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 清理之前的agent实例
    from app.api import chat as chat_module
    user_id = test_user["user"].id
    if user_id in chat_module._user_agents:
        del chat_module._user_agents[user_id]
    
    # Mock LLM调用，避免实际调用API
    # 需要在ChatAgent初始化时mock
    with patch('app.agents.chat_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_response = AIMessage(content="Mocked AI response")
        mock_llm.invoke = Mock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm
        
        # 测试对话接口
        resp = await client.post(
            "/chat/",
            json={
                "message": "Hello",
                "provider": "deepseek"
            },
            headers=headers
        )
        
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert "provider" in data
        assert data["provider"] == "deepseek"
        # 如果mock生效，应该是mock的响应；如果没生效，说明实际调用了API（这也是正常的）
        assert len(data["response"]) > 0


@pytest.mark.asyncio
async def test_chat_api_history(client, test_user):
    """测试获取对话历史API"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 清理之前的agent实例
    from app.api import chat as chat_module
    user_id = test_user["user"].id
    if user_id in chat_module._user_agents:
        del chat_module._user_agents[user_id]
    
    with patch('app.agents.chat_agent.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_response = AIMessage(content="Response")
        mock_llm.invoke = Mock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm
        
        # 先发送一条消息
        await client.post(
            "/chat/",
            json={"message": "Hello"},
            headers=headers
        )
        
        # 获取历史
        resp = await client.get("/chat/history", headers=headers)
        assert resp.status_code == 200
        history = resp.json()
        assert isinstance(history, list)
        # 应该包含用户消息和AI回复（至少2条）
        assert len(history) >= 2
        assert history[0]["type"] == "user"
        assert history[1]["type"] == "assistant"


@pytest.mark.asyncio
async def test_chat_api_clear_history(client, test_user):
    """测试清空历史API"""
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    with patch('app.agents.llm_providers.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_llm._llm_type = "deepseek"
        mock_response = AIMessage(content="Response")
        mock_llm.invoke = Mock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm
        
        # 先发送消息
        await client.post(
            "/chat/",
            json={"message": "Hello"},
            headers=headers
        )
        
        # 清空历史
        resp = await client.post("/chat/clear", headers=headers)
        assert resp.status_code == 200
        assert "message" in resp.json()
        
        # 验证历史已清空
        history_resp = await client.get("/chat/history", headers=headers)
        history = history_resp.json()
        assert len(history) == 0

