"""
任务管理 API - 展示如何通过 REST API 提交和管理异步任务
学习要点：API 层与任务层的解耦，异步任务的生命周期管理
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from app.models.task import TaskRequest, TaskResponse, TaskStatus
from app.core.logger import get_logger
from app.tasks.video_tasks import (
    process_video_subtitles,
    detect_language_only
)

logger = get_logger(__name__)
router = APIRouter()


@router.post("/submit", response_model=TaskResponse)
async def submit_task(task_request: TaskRequest) -> TaskResponse:
    """
    提交视频字幕处理任务
    
    这是学习的核心：如何将 HTTP 请求转换为异步任务
    """
    try:
        logger.info(f"📥 收到任务提交请求: video_id={task_request.video_id}")
        
        # 提交异步任务到 Celery
        # 这里是关键：API 层不直接处理业务逻辑，而是委托给任务队列
        task = process_video_subtitles.delay(
            video_id=task_request.video_id,
            subtitles=task_request.subtitles
        )
        
        logger.info(f"🎯 任务已提交到队列: task_id={task.id}")
        
        return TaskResponse(
            task_id=task.id,
            video_id=task_request.video_id,
            status="pending",
            message="任务已提交，正在处理中..."
        )
        
    except Exception as e:
        logger.error(f"❌ 任务提交失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"任务提交失败: {str(e)}"
        )


@router.post("/detect-language", response_model=TaskResponse)
async def detect_language(request: TaskRequest) -> TaskResponse:
    """
    提交语言检测任务（单步任务示例）
    
    展示如何提交不同类型的任务
    """
    try:
        logger.info(f"🔍 收到语言检测请求: video_id={request.video_id}")
        
        # 提交语言检测任务
        task = detect_language_only.delay(
            video_id=request.video_id,
            subtitles=request.subtitles
        )
        
        return TaskResponse(
            task_id=task.id,
            video_id=request.video_id,
            status="pending",
            message="语言检测任务已提交"
        )
        
    except Exception as e:
        logger.error(f"❌ 语言检测任务提交失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"语言检测任务提交失败: {str(e)}"
        )


@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str) -> TaskStatus:
    """
    查询任务状态
    
    学习要点：如何查询异步任务的执行状态和结果
    """
    try:
        # 从 Celery 获取任务状态
        from app.core.celery_app import celery_app
        task = celery_app.AsyncResult(task_id)
        
        # 构建状态响应
        if task.state == "PENDING":
            status_info = {
                "task_id": task_id,
                "status": "pending",
                "message": "任务正在等待执行"
            }
        elif task.state == "PROGRESS":
            status_info = {
                "task_id": task_id,
                "status": "running",
                "message": "任务正在执行中",
                "progress": task.info.get("progress", 0) if task.info else 0
            }
        elif task.state == "SUCCESS":
            result = task.result or {}
            status_info = {
                "task_id": task_id,
                "status": "completed",
                "message": "任务执行成功",
                "result": result
            }
        elif task.state == "FAILURE":
            status_info = {
                "task_id": task_id,
                "status": "failed",
                "message": f"任务执行失败: {str(task.info)}",
                "error": str(task.info)
            }
        else:
            status_info = {
                "task_id": task_id,
                "status": task.state.lower(),
                "message": f"任务状态: {task.state}"
            }
        
        logger.info(f"📊 查询任务状态: {task_id} -> {status_info['status']}")
        return TaskStatus(**status_info)
        
    except Exception as e:
        logger.error(f"❌ 查询任务状态失败: task_id={task_id}, error={e}")
        raise HTTPException(
            status_code=500,
            detail=f"查询任务状态失败: {str(e)}"
        )


@router.get("/list")
async def list_active_tasks() -> Dict[str, Any]:
    """
    获取活跃任务列表
    
    这是额外的功能，展示如何监控任务队列
    """
    try:
        from app.core.celery_app import celery_app
        
        # 获取活跃任务
        active_tasks = celery_app.control.inspect().active()
        
        # 处理返回格式
        task_list = []
        if active_tasks:
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    task_list.append({
                        "task_id": task["id"],
                        "name": task["name"],
                        "worker": worker,
                        "args": task.get("args", []),
                        "kwargs": task.get("kwargs", {})
                    })
        
        return {
            "active_tasks": task_list,
            "count": len(task_list),
            "message": f"当前有 {len(task_list)} 个活跃任务"
        }
        
    except Exception as e:
        logger.error(f"❌ 获取活跃任务列表失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取活跃任务列表失败: {str(e)}"
        )
