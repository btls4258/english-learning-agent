# backend/app/agents/english_learning_agent.py
"""
英语学习Agent - 使用LangChain v1.0架构重构
符合主流规范的Agent实现，支持工具调用和复杂学习流程
"""

from typing import Dict, Any, Optional, List
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.agents.llm_providers import get_llm
from app.agents.tools import learning_tools


class EnglishLearningAgent:
    """
    英语学习Agent - 基于LangChain v1.0架构
    支持工具调用、记忆管理和个性化学习
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ):
        """
        初始化英语学习Agent

        Args:
            provider: LLM提供商
            user_context: 用户上下文信息
        """
        self.llm = get_llm(provider=provider)
        self.provider = provider or "default"
        self.user_context = user_context or {}

        # 构建系统提示词
        self.system_prompt = self._build_system_prompt()

        # 获取所有学习工具
        self.tools = self._get_available_tools()

        # 创建Agent
        self.agent = self._create_agent()

        # 对话历史（用于上下文管理）
        self.conversation_history: List[HumanMessage | AIMessage] = []

    def _build_system_prompt(self) -> str:
        """构建Agent的系统提示词"""
        base_prompt = """
你是一位专业的英语学习AI助教，名叫Emma。你的使命是帮助用户高效地学习英语，提供个性化的学习体验。

**你的核心职责：**
1. 📚 **词汇教学** - 解释单词含义、用法、搭配和例句
2. 🎯 **语法指导** - 清晰解释语法规则，提供实用例句
3. 💬 **口语练习** - 创造对话场景，帮助用户练习实际交流
4. 📝 **练习生成** - 根据用户水平创建合适的练习题
5. 📊 **进度跟踪** - 监控学习进度，推荐复习内容
6. 🔧 **个性化辅导** - 根据用户学习习惯调整教学方法

**教学理念：**
- 鼓励为主，耐心指导
- 实用性强，联系实际场景
- 循序渐进，螺旋式上升
- 及时反馈，纠正错误

**交互风格：**
- 友好亲切，像真正的老师
- 中英文混合，以帮助理解
- 举例丰富，便于掌握
- 互动性强，激发学习兴趣

**工具使用指南：**
- 当需要查询单词时，使用 search_dictionary
- 需要创建练习时，使用 create_vocabulary_exercise
- 查看学习进度时，使用 get_user_progress
- 创建对话练习时，使用 create_conversation_practice
- 需要发音指导时，使用 search_pronunciation
- 语法问题时，使用 get_grammar_explanation

现在开始你的教学吧！记住，每个学生都是独特的，需要你的用心指导。💪✨
        """.strip()

        # 添加个性化信息
        if self.user_context:
            user_level = self.user_context.get("level", "intermediate")
            user_goals = self.user_context.get("goals", [])

            if user_goals:
                goals_text = "、".join(user_goals)
                base_prompt += f"\n\n**用户学习目标：** {goals_text}"

            base_prompt += f"\n\n**用户英语水平：** {user_level}"
            base_prompt += "\n请根据用户的水平调整教学难度和内容深度。"

        return base_prompt

    def _get_available_tools(self) -> List:
        """获取可用的学习工具列表"""
        return [
            learning_tools.search_dictionary,
            learning_tools.get_word_definitions,
            learning_tools.create_vocabulary_exercise,
            learning_tools.get_user_progress,
            learning_tools.get_review_words,
            learning_tools.mark_word_completed,
            learning_tools.search_pronunciation,
            learning_tools.get_grammar_explanation,
            learning_tools.create_conversation_practice
        ]

    def _create_agent(self):
        """创建LangChain Agent实例"""
        # 创建Agent执行器 - 使用正确的LangChain v1.0语法
        agent = create_agent(
            self.llm,
            self.tools,
            system_prompt=self.system_prompt
        )

        return agent

    def set_learning_context(self, db_session, user_id: int):
        """
        设置学习上下文（数据库会话和用户ID）

        Args:
            db_session: 数据库会话
            user_id: 用户ID
        """
        learning_tools.set_learning_context(db_session, user_id)
        self.user_context["user_id"] = user_id

    def chat(
        self,
        user_input: str,
        system_prompt: Optional[str] = None,
        clear_history: bool = False
    ) -> str:
        """
        与Agent进行对话

        Args:
            user_input: 用户输入
            system_prompt: 可选的系统提示词覆盖
            clear_history: 是否清空历史记录

        Returns:
            Agent的回复内容
        """
        # 清空历史记录（如果需要）
        if clear_history:
            self.conversation_history.clear()

        # 创建当前用户消息
        human_message = HumanMessage(content=user_input)

        try:
            # 使用创建的Agent进行对话 - LangChain v1.0标准方式
            # 构建消息列表
            messages = []

            # 添加历史对话（转换为标准格式）
            for msg in self.conversation_history:
                if isinstance(msg, HumanMessage):
                    messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages.append({"role": "assistant", "content": msg.content})

            # 添加当前用户输入
            messages.append({"role": "user", "content": user_input})

            # 使用Agent调用
            response = self.agent.invoke({"messages": messages})

            # 从响应中获取AI回复内容 - 处理LangChain v1.0的响应格式
            if isinstance(response, dict) and "messages" in response:
                # 标准格式：{"messages": [...]}
                ai_messages = response["messages"]
                if ai_messages and len(ai_messages) > 0:
                    last_message = ai_messages[-1]
                    if isinstance(last_message, dict) and "content" in last_message:
                        ai_response = last_message["content"]
                    elif hasattr(last_message, 'content'):
                        ai_response = last_message.content
                    else:
                        ai_response = str(last_message)
                else:
                    ai_response = "抱歉，我没有收到有效的响应。"
            elif hasattr(response, 'content'):
                # 直接是消息对象
                ai_response = response.content
            elif isinstance(response, str):
                # 直接是字符串
                ai_response = response
            else:
                # 其他情况，尝试转换为字符串
                ai_response = str(response)
                print(f"Agent响应格式异常: {type(response)} - {response}")

            # 创建AI消息
            ai_message = AIMessage(content=ai_response)

            # 更新对话历史
            self.conversation_history.append(human_message)
            self.conversation_history.append(ai_message)

            return ai_response

        except Exception as e:
            error_msg = f"处理您的请求时出现错误：{str(e)}"
            print(f"Agent错误: {e}")  # 调试用

            # 即使出错也要更新历史记录
            self.conversation_history.append(human_message)
            self.conversation_history.append(AIMessage(content=error_msg))

            return error_msg

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()

    def get_history(self) -> List[HumanMessage | AIMessage]:
        """获取对话历史"""
        return self.conversation_history.copy()

    def get_user_context(self) -> Dict[str, Any]:
        """获取用户上下文"""
        return self.user_context.copy()

    def update_user_context(self, **kwargs):
        """更新用户上下文"""
        self.user_context.update(kwargs)
        # 重新构建系统提示词以反映更新
        self.system_prompt = self._build_system_prompt()
        # 重新创建Agent以使用新的提示词
        self.agent = self._create_agent()

    def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            "provider": self.provider,
            "tools_count": len(self.tools),
            "tools": [tool.name for tool in self.tools],
            "conversation_length": len(self.conversation_history),
            "user_context": self.user_context
        }


class AgentManager:
    """
    Agent管理器 - 负责创建和管理多个用户的Agent实例
    在实际生产环境中，应该使用Redis或其他缓存系统
    """

    def __init__(self):
        self._agents: Dict[int, EnglishLearningAgent] = {}

    def get_agent(
        self,
        user_id: int,
        provider: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> EnglishLearningAgent:
        """
        获取或创建用户的Agent实例

        Args:
            user_id: 用户ID
            provider: LLM提供商
            user_context: 用户上下文

        Returns:
            EnglishLearningAgent实例
        """
        if user_id not in self._agents:
            self._agents[user_id] = EnglishLearningAgent(
                provider=provider,
                user_context=user_context
            )
        elif provider:
            # 如果指定了不同的provider，重新创建Agent
            current_agent = self._agents[user_id]
            if current_agent.provider != provider:
                self._agents[user_id] = EnglishLearningAgent(
                    provider=provider,
                    user_context=user_context or current_agent.get_user_context()
                )

        return self._agents[user_id]

    def remove_agent(self, user_id: int):
        """移除用户的Agent实例"""
        if user_id in self._agents:
            del self._agents[user_id]

    def get_all_agents_info(self) -> Dict[int, Dict[str, Any]]:
        """获取所有Agent的信息"""
        return {
            user_id: agent.get_agent_info()
            for user_id, agent in self._agents.items()
        }

    def clear_all_agents(self):
        """清空所有Agent实例"""
        self._agents.clear()


# 全局Agent管理器实例
agent_manager = AgentManager()