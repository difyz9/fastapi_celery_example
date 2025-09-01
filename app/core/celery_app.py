"""
Celery应用配置
"""
from celery import Celery
from app.core.config import settings

# 创建Celery应用
celery_app = Celery(
    "video_processor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.video_tasks"]  # 包含任务模块
)

# Celery配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区设置
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务结果过期时间
    result_expires=settings.TASK_TIMEOUT,
    
    # 任务路由
    task_routes={
        "app.tasks.video_tasks.process_subtitles": {"queue": "subtitle_queue"},
        "app.tasks.video_tasks.detect_language_simple": {"queue": "detect_queue"},
    },
    
    # 工作进程配置
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # 任务重试配置
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=settings.MAX_RETRIES,
    
    # 监控配置
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# 自动发现任务
celery_app.autodiscover_tasks()
