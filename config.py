# config.py - 项目配置管理
import os
from typing import Dict, Any

class CeleryConfig:
    """Celery配置类"""
    
    # Redis配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    
    # 构建Redis URL
    if REDIS_PASSWORD:
        BROKER_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        RESULT_BACKEND = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    else:
        BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # Celery配置
    TASK_SERIALIZER = 'json'
    RESULT_SERIALIZER = 'json'
    ACCEPT_CONTENT = ['json']
    TIMEZONE = 'UTC'
    ENABLE_UTC = True
    
    # 任务路由配置
    TASK_ROUTES = {
        'tasks.math_tasks.*': {'queue': 'math'},
        'tasks.data_tasks.*': {'queue': 'data'},
        'tasks.io_tasks.*': {'queue': 'io'},
        'workflows.*': {'queue': 'workflows'},
    }
    
    # 任务结果过期时间（秒）
    RESULT_EXPIRES = 3600
    
    # 工作进程配置
    WORKER_PREFETCH_MULTIPLIER = 1
    TASK_ACKS_LATE = True
    
    # 任务时间限制
    TASK_TIME_LIMIT = 300  # 5分钟
    TASK_SOFT_TIME_LIMIT = 240  # 4分钟
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """获取Celery配置字典"""
        return {
            'broker_url': cls.BROKER_URL,
            'result_backend': cls.RESULT_BACKEND,
            'task_serializer': cls.TASK_SERIALIZER,
            'result_serializer': cls.RESULT_SERIALIZER,
            'accept_content': cls.ACCEPT_CONTENT,
            'timezone': cls.TIMEZONE,
            'enable_utc': cls.ENABLE_UTC,
            'task_routes': cls.TASK_ROUTES,
            'result_expires': cls.RESULT_EXPIRES,
            'worker_prefetch_multiplier': cls.WORKER_PREFETCH_MULTIPLIER,
            'task_acks_late': cls.TASK_ACKS_LATE,
            'task_time_limit': cls.TASK_TIME_LIMIT,
            'task_soft_time_limit': cls.TASK_SOFT_TIME_LIMIT,
        }

class AppConfig:
    """应用程序配置"""
    
    # 应用名称
    APP_NAME = 'task_chain_system'
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 开发/生产环境
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
