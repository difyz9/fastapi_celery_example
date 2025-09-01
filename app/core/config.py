"""
简化的应用配置 - 学习案例
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置 - 保持简洁，专注核心概念"""
    
    # 基础配置
    APP_NAME: str = "任务链学习案例"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API 配置
    API_V1_STR: str = "/api/v1"
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_DB: str = "0"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery 配置（学习重点）
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0") 
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # 任务配置
    TASK_TIMEOUT: str = "3600"
    MAX_RETRIES: str = "3"
    MAX_FILE_SIZE: str = "50"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"


# 全局配置实例
settings = Settings()
