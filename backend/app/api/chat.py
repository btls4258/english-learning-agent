# backend/app/api/chat.py
"""
对话相关的API路由
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from app.models import User
from app.dependencies import get_current_user
from app.agents.chat_agent import ChatAgent
from langchain_core.messages import HumanMessage, SystemMessage 

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """对话请求模型"""
    message: str
    provider: Optional[str] = None  # 可选：指定使用的LLM提供商
    clear_history: Optional[bool] = False  # 可选：是否清空历史


class ChatResponse(BaseModel):
    """对话响应模型"""
    response: str
    provider: str  # 实际使用的LLM提供商


# 注意：这里使用字典存储每个用户的Agent实例
# 在生产环境中，应该使用Redis或其他持久化存储
_user_agents: dict[int, ChatAgent] = {}


def get_user_agent(user_id: int, provider: Optional[str] = None) -> ChatAgent:
    """
    获取或创建用户的ChatAgent实例
    
    Args:
        user_id: 用户ID
        provider: LLM提供商
    
    Returns:
        ChatAgent实例
    """
    if user_id not in _user_agents:
        _user_agents[user_id] = ChatAgent(provider=provider)
    elif provider:
        # 如果指定了provider且与当前不同，创建新的Agent
        current_provider = _user_agents[user_id].llm._llm_type
        if current_provider != provider:
            _user_agents[user_id] = ChatAgent(provider=provider)
    
    return _user_agents[user_id]


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    对话接口
    
    接收用户消息，返回AI回复
    """
    try:
        # 获取用户的Agent实例
        agent = get_user_agent(current_user.id, provider=request.provider)
        
        # 如果需要清空历史
        if request.clear_history:
            agent.clear_history()
        
        # 调用Agent进行对话
        response_text = agent.chat(request.message)
        
        # 获取实际使用的provider
        provider_used = agent.llm._llm_type
        
        return ChatResponse(
            response=response_text,
            provider=provider_used
        )
    
    except ValueError as e:
        # 处理配置错误（如API Key未设置）
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # 处理其他错误
        raise HTTPException(status_code=500, detail=f"对话处理失败: {str(e)}")


@router.post("/clear", response_model=dict)
async def clear_chat_history(
    current_user: User = Depends(get_current_user)
):
    """
    清空当前用户的对话历史
    """
    if current_user.id in _user_agents:
        _user_agents[current_user.id].clear_history()
        return {"message": "对话历史已清空"}
    return {"message": "没有对话历史需要清空"}


@router.get("/history", response_model=List[dict])
async def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的对话历史
    """
    if current_user.id not in _user_agents:
        return []
    
    agent = _user_agents[current_user.id]
    history = agent.get_history()
    
    # 转换为字典格式返回
    result = []
    for msg in history:
        if isinstance(msg, HumanMessage):
            msg_type = "user"
        elif isinstance(msg, SystemMessage):
            msg_type = "system"
        else:
            msg_type = "assistant"
        
        result.append({
            "type": msg_type,
            "content": msg.content
        })
    
    return result