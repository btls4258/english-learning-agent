# backend/app/api/chat.py
"""
对话相关的API路由 - 英语学习Agent
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.dependencies import get_current_user, get_db
from app.agents.english_learning_agent import EnglishLearningAgent, agent_manager
from langchain_core.messages import HumanMessage, SystemMessage

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """对话请求模型"""
    message: str
    provider: Optional[str] = None  # 可选：指定使用的LLM提供商
    clear_history: Optional[bool] = False  # 可选：是否清空历史
    user_context: Optional[Dict[str, Any]] = None  # 可选：用户上下文信息


class ChatResponse(BaseModel):
    """对话响应模型"""
    response: str
    provider: str  # 实际使用的LLM提供商
    tools_used: Optional[List[str]] = None  # 使用的工具列表
    session_info: Optional[Dict[str, Any]] = None  # 会话信息


class AgentInfoResponse(BaseModel):
    """Agent信息响应模型"""
    provider: str
    tools_count: int
    tools: List[str]
    conversation_length: int
    user_context: Dict[str, Any]


def get_user_agent(
    user_id: int,
    provider: Optional[str] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> EnglishLearningAgent:
    """
    获取或创建用户的英语学习Agent实例

    Args:
        user_id: 用户ID
        provider: LLM提供商
        user_context: 用户上下文信息

    Returns:
        EnglishLearningAgent实例
    """
    return agent_manager.get_agent(
        user_id=user_id,
        provider=provider,
        user_context=user_context
    )


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    对话接口 - 使用新的英语学习Agent

    接收用户消息，返回AI回复，支持工具调用
    """
    try:
        # 获取用户的Agent实例
        agent = get_user_agent(
            current_user.id,
            provider=request.provider,
            user_context=request.user_context
        )

        # 设置学习上下文（数据库会话和用户ID）
        agent.set_learning_context(db, current_user.id)

        # 如果需要清空历史
        if request.clear_history:
            agent.clear_history()

        # 调用Agent进行对话
        response_text = agent.chat(
            user_input=request.message,
            clear_history=request.clear_history
        )

        # 获取Agent信息
        agent_info = agent.get_agent_info()
        tools_used = []  # 可以从响应中提取实际使用的工具

        return ChatResponse(
            response=response_text,
            provider=agent_info["provider"],
            tools_used=tools_used,
            session_info={
                "conversation_length": agent_info["conversation_length"],
                "tools_available": agent_info["tools"]
            }
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
    agent = get_user_agent(current_user.id)
    agent.clear_history()
    return {"message": "对话历史已清空"}


@router.get("/history", response_model=List[dict])
async def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的对话历史
    """
    agent = get_user_agent(current_user.id)
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


@router.get("/agent-info", response_model=AgentInfoResponse)
async def get_agent_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的Agent信息
    """
    agent = get_user_agent(current_user.id)
    info = agent.get_agent_info()

    return AgentInfoResponse(
        provider=info["provider"],
        tools_count=info["tools_count"],
        tools=info["tools"],
        conversation_length=info["conversation_length"],
        user_context=info["user_context"]
    )


@router.post("/update-context", response_model=dict)
async def update_user_context(
    context_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    更新用户上下文信息
    """
    agent = get_user_agent(current_user.id)
    agent.update_user_context(**context_data)

    return {
        "message": "用户上下文已更新",
        "updated_context": context_data
    }


@router.get("/tools", response_model=List[dict])
async def get_available_tools():
    """
    获取所有可用的学习工具
    """
    from app.agents.tools import learning_tools

    tools_info = []
    for tool_func in learning_tools.__all__:
        tool_obj = getattr(learning_tools, tool_func)
        if hasattr(tool_obj, 'name') and hasattr(tool_obj, 'description'):
            tools_info.append({
                "name": tool_obj.name,
                "description": tool_obj.description,
                "function": tool_func
            })

    return tools_info