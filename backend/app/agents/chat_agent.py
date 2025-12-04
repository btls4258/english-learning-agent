# backend/app/agents/chat_agent.py
"""
基础对话Agent实现
使用LangChain v1.0的架构，先实现非流式对话
"""
from typing import List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from app.agents.llm_providers import get_llm


class ChatAgent:
    """
    基础对话Agent
    负责管理对话上下文和调用LLM
    """
    
    def __init__(self, provider: Optional[str] = None):
        """
        初始化ChatAgent
        
        Args:
            provider: LLM提供商名称 ("deepseek" 或 "glm4")，默认使用配置中的值
        """
        self.llm = get_llm(provider=provider)
        self.conversation_history: List[BaseMessage] = []
    
    def chat(self, user_input: str, system_prompt: Optional[str] = None) -> str:
        """
        非流式对话方法
        
        Args:
            user_input: 用户输入
            system_prompt: 可选的系统提示词（只在第一次对话时添加）
        
        Returns:
            AI的回复内容
        """
        # 如果是第一次对话且有system_prompt，添加到历史记录
        if system_prompt and len(self.conversation_history) == 0:
            system_message = SystemMessage(content=system_prompt)
            self.conversation_history.append(system_message)
        
        # 添加用户消息到历史记录
        user_message = HumanMessage(content=user_input)
        self.conversation_history.append(user_message)
        
        # 调用LLM生成回复
        # BaseChatModel的invoke方法返回AIMessage
        response = self.llm.invoke(self.conversation_history)
        
        # 提取回复内容（invoke返回的就是AIMessage）
        ai_content = response.content
        
        # 添加AI回复到历史记录
        ai_message = AIMessage(content=ai_content)
        self.conversation_history.append(ai_message)
        
        return ai_content
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def get_history(self) -> List[BaseMessage]:
        """获取对话历史"""
        return self.conversation_history.copy()