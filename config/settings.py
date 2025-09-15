"""
Configuration settings for NTBK_AI service
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Security settings
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Model settings
    MODEL_NAME: str = Field(default="google/flan-t5-small", env="MODEL_NAME")
    MODEL_CACHE_DIR: str = Field(default="./model_cache", env="MODEL_CACHE_DIR")
    MAX_CONCURRENT_TASKS: int = Field(default=10, env="MAX_CONCURRENT_TASKS")
    
    # Task management settings
    TASK_TIMEOUT: int = Field(default=300, env="TASK_TIMEOUT")  # 5 minutes
    TASK_CLEANUP_INTERVAL: int = Field(default=3600, env="TASK_CLEANUP_INTERVAL")  # 1 hour
    MAX_TASK_HISTORY: int = Field(default=1000, env="MAX_TASK_HISTORY")
    
    # Redis settings (for task state management)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # External tool settings
    EXTERNAL_TOOL_TIMEOUT: int = Field(default=30, env="EXTERNAL_TOOL_TIMEOUT")
    MAX_TOOL_RETRIES: int = Field(default=3, env="MAX_TOOL_RETRIES")
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
