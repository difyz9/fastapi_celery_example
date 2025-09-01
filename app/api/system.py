"""
健康检查和系统信息API
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import redis
from app.core.config import settings
from app.core.celery_app import celery_app
from app.models.schemas import HealthResponse
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["系统"])


@router.get("/health", response_model=HealthResponse, summary="健康检查")
def health_check():
    """
    系统健康检查
    
    检查以下组件的状态：
    - API服务状态
    - Celery工作进程状态
    - Redis连接状态
    """
    try:
        # 检查Redis连接
        redis_status = "unknown"
        try:
            r = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                socket_timeout=5
            )
            r.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = f"unhealthy: {str(e)}"
        
        # 检查Celery工作进程
        celery_status = "unknown"
        try:
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()
            if active_workers:
                celery_status = "healthy"
            else:
                celery_status = "no_workers"
        except Exception as e:
            celery_status = f"unhealthy: {str(e)}"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "celery_status": celery_status,
            "redis_status": redis_status
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.get("/", summary="根路径")
def read_root():
    """
    API根路径，返回基本信息
    """
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api": settings.API_V1_STR
    }


@router.get("/info", summary="系统信息")
def get_system_info():
    """
    获取系统配置信息
    """
    try:
        # 获取Celery信息
        inspect = celery_app.control.inspect()
        active_workers = inspect.active() or {}
        registered_tasks = inspect.registered() or {}
        
        # 统计信息
        worker_count = len(active_workers)
        task_count = sum(len(tasks) for tasks in registered_tasks.values()) if registered_tasks else 0
        
        return {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "debug": settings.DEBUG,
            "celery": {
                "broker_url": settings.CELERY_BROKER_URL.split('@')[-1] if '@' in settings.CELERY_BROKER_URL else settings.CELERY_BROKER_URL,
                "result_backend": settings.CELERY_RESULT_BACKEND.split('@')[-1] if '@' in settings.CELERY_RESULT_BACKEND else settings.CELERY_RESULT_BACKEND,
                "worker_count": worker_count,
                "registered_tasks": task_count,
                "active_workers": list(active_workers.keys()) if active_workers else []
            },
            "redis": {
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
                "db": settings.REDIS_DB
            },
            "limits": {
                "max_file_size": f"{settings.MAX_FILE_SIZE // (1024*1024)}MB",
                "task_timeout": f"{settings.TASK_TIMEOUT}s",
                "max_retries": settings.MAX_RETRIES
            }
        }
        
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统信息失败: {str(e)}")
