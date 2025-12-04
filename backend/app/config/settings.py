# backend/app/config/settings.py
"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # LLM配置
    DEEPSEEK_API_KEY: Optional[str] = None
    GLM4_API_KEY: Optional[str] = None
    GLM4_API_BASE: Optional[str] = None
    
    # 默认使用的LLM提供商
    DEFAULT_LLM_PROVIDER: str = "deepseek"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 忽略.env中未定义的字段，避免验证错误


settings = Settings()