# backend/app/agents/llm_providers.py
"""
LLM提供商封装模块
支持DeepSeek和GLM4.6的调用
LangChain v1.0 兼容版本
"""
from typing import Optional, Dict, Any, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
import httpx
from app.config.settings import settings


class DeepSeekChatModel(BaseChatModel):
    """
    DeepSeek模型封装，继承LangChain v1.0的BaseChatModel
    使用ChatModel而不是LLM，支持消息格式
    """
    api_key: str
    api_base: str = "https://api.deepseek.com/v1"
    model_name: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    @property
    def _llm_type(self) -> str:
        return "deepseek"

    def bind_tools(self, tools, **kwargs) -> "DeepSeekChatModel":
        """
        绑定工具到模型
        """
        # 暂时返回自身，工具调用将在工具层面处理
        return self
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        LangChain v1.0 使用 _generate 方法
        接收消息列表，返回ChatResult
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 将LangChain消息格式转换为API格式
        api_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                api_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                api_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                api_messages.append({"role": "assistant", "content": msg.content})
            else:
                # 处理其他类型的消息
                api_messages.append({"role": "user", "content": str(msg.content)})
        payload = {
            "model": self.model_name,
            "messages": api_messages,
            "temperature": self.temperature,
        }
        
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
        
        if stop:
            payload["stop"] = stop
        
        api_url = f"{self.api_base}/chat/completions"
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(api_url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                # 检查API返回的错误
                if "error" in result:
                    error_msg = result["error"].get("message", "Unknown API error")
                    raise ValueError(f"DeepSeek API错误: {error_msg}")
                
                # 检查返回格式
                if "choices" not in result or len(result["choices"]) == 0:
                    raise ValueError("DeepSeek API返回格式错误：没有choices字段")
                
                choice = result["choices"][0]
                message_data = choice["message"]
                finish_reason = choice.get("finish_reason", "")
                
                # 根据finish_reason提取内容
                # 如果finish_reason是"thinking"，从reasoning_content提取
                if finish_reason == "thinking":
                    content = message_data.get("reasoning_content", "")
                    if not content:
                        # 如果reasoning_content也为空，尝试使用content
                        content = message_data.get("content") or ""
                else:
                    # 正常情况，从content提取
                    content = message_data.get("content") or ""
                
                # 如果内容为空，抛出错误
                if not content:
                    raise ValueError(f"DeepSeek API返回内容为空，finish_reason: {finish_reason}")
                
                # 构造ChatResult
                message = AIMessage(content=content)
                generation = ChatGeneration(message=message)
                return ChatResult(generations=[generation])
        
        except httpx.HTTPStatusError as e:
            raise ValueError(f"DeepSeek API HTTP错误: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"DeepSeek API请求错误: {str(e)}")
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "api_base": self.api_base,
        }


class GLM4ChatModel(BaseChatModel):
    """
    GLM4.6模型封装
    LangChain v1.0 兼容版本
    """
    api_key: str
    api_base: str  # 完整API地址
    model_name: str = "glm-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    @property
    def _llm_type(self) -> str:
        return "glm4"

    def bind_tools(self, tools, **kwargs) -> "GLM4ChatModel":
        """
        绑定工具到模型
        """
        # 暂时返回自身，工具调用将在工具层面处理
        return self
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        调用GLM4 API
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 转换消息格式
        api_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                api_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                api_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                api_messages.append({"role": "assistant", "content": msg.content})
            else:
                api_messages.append({"role": "user", "content": str(msg.content)})
        payload = {
            "model": self.model_name,
            "messages": api_messages,
            "temperature": self.temperature,
        }
        
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
        
        if stop:
            payload["stop"] = stop
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.api_base, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                # 检查API返回的错误
                if "error" in result:
                    error_msg = result["error"].get("message", "Unknown API error")
                    raise ValueError(f"GLM4 API错误: {error_msg}")
                
                # 检查返回格式
                if "choices" not in result or len(result["choices"]) == 0:
                    raise ValueError("GLM4 API返回格式错误：没有choices字段")
                
                content = result["choices"][0]["message"].get("content") or ""
                
                if not content:
                    raise ValueError("GLM4 API返回内容为空")
                
                message = AIMessage(content=content)
                generation = ChatGeneration(message=message)
                return ChatResult(generations=[generation])
        
        except httpx.HTTPStatusError as e:
            raise ValueError(f"GLM4 API HTTP错误: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"GLM4 API请求错误: {str(e)}")
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "api_base": self.api_base,
        }


def get_llm(provider: Optional[str] = None) -> BaseChatModel:
    """
    工厂函数：根据provider名称返回对应的ChatModel实例
    
    Args:
        provider: "deepseek" 或 "glm4"，如果为None则使用配置中的默认值
    
    Returns:
        BaseChatModel实例（LangChain v1.0兼容）
    """
    if provider is None:
        provider = settings.DEFAULT_LLM_PROVIDER
    
    provider = provider.lower()
    
    if provider == "deepseek":
        api_key = settings.DEEPSEEK_API_KEY
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY环境变量未设置，请在.env文件中配置")
        return DeepSeekChatModel(api_key=api_key)
    
    elif provider == "glm4":
        api_key = settings.GLM4_API_KEY
        api_base = settings.GLM4_API_BASE
        if not api_key:
            raise ValueError("GLM4_API_KEY环境变量未设置，请在.env文件中配置")
        if not api_base:
            raise ValueError("GLM4_API_BASE环境变量未设置，请在.env文件中配置")
        return GLM4ChatModel(api_key=api_key, api_base=api_base)
    
    else:
        raise ValueError(f"不支持的provider: {provider}，支持的值：deepseek, glm4")