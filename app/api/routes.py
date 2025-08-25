# app/api/routes.py - 主路由聚合器
from fastapi import APIRouter
from app.services.math_chain_service import MathChainService
from app.services.bilibili_chain_service import BilibiliChainService

# 创建主路由器
router = APIRouter()

# 服务实例
math_chain_service = MathChainService()
bilibili_chain_service = BilibiliChainService()

@router.get("/")
async def root():
    """根路径，返回API信息"""
    # 合并两个服务的链信息
    all_chains = {
        "math_chains": math_chain_service.get_available_chains(),
        "bilibili_chains": bilibili_chain_service.get_available_chains()
    }
    
    return {
        "message": "任务链处理API - 支持数学运算和Bilibili视频处理",
        "version": "2.0.0",
        "architecture": "独立app层架构 + SQLAlchemy ORM + 模块化路由 + 分离服务",
        "available_chains": all_chains,
        "endpoints": {
            "数学任务": {
                "submit_math_task": "/math/submit",
                "get_math_chains": "/math/chains"
            },
            "Bilibili视频处理": {
                "submit_bilibili_task": "/bilibili/submit",
                "get_bilibili_chains": "/bilibili/chains",
                "get_video_info": "/bilibili/video/{bvid}/info"
            },
            "任务管理": {
                "get_task_status": "/tasks/{task_id}/status",
                "get_task_result": "/tasks/{task_id}/result",
                "list_tasks": "/tasks",
                "get_statistics": "/tasks/statistics",
                "get_tasks_by_status": "/tasks/status/{status}",
                "delete_task": "/tasks/{task_id}"
            },
            "系统信息": {
                "api_info": "/",
                "all_chains": "/chains",
                "health_check": "/health"
            }
        }
    }

@router.get("/chains")
async def get_all_chains():
    """获取所有可用的任务链"""
    return {
        "math_chains": math_chain_service.get_available_chains(),
        "bilibili_chains": bilibili_chain_service.get_available_chains(),
        "total_chains": {
            "math": len(math_chain_service.get_available_chains()),
            "bilibili": len(bilibili_chain_service.get_available_chains())
        }
    }

@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "Task Chain API",
        "version": "2.0.0",
        "components": {
            "database": "SQLAlchemy ORM",
            "message_broker": "Redis",
            "task_queue": "Celery",
            "web_framework": "FastAPI"
        }
    }
