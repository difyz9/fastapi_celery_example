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
async def detect_language(video_id: int, subtitles: List[Dict[str, Any]]) -> TaskResponse:
    """
    提交语言检测任务（单步任务示例）
    
    展示如何提交不同类型的任务
    """
    try:
        logger.info(f"🔍 收到语言检测请求: video_id={video_id}")
        
        # 提交语言检测任务
        task = detect_language_only.delay(
            video_id=video_id,
            subtitles=subtitles
        )
        
        return TaskResponse(
            task_id=task.id,
            video_id=video_id,
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


@router.post("/submit", response_model=TaskResponse, summary="提交处理任务")
def submit_task(request: TaskSubmitRequest):
    """
    提交视频处理任务
    
    - **video_id**: 视频ID
    - **subtitles**: 字幕数据列表
    - **platform**: 平台类型 (bilibili/youtube/tiktok)
    - **task_type**: 任务类型 (full/detect/translate/audio_generate)
    """
    try:
        # 转换字幕数据
        subtitles_data = [sub.dict() for sub in request.subtitles]
        
        # 提交任务
        result = task_service.submit_task(
            video_id=request.video_id,
            subtitles=subtitles_data,
            platform=request.platform,
            task_type=request.task_type
        )
        
        return result
        
    except Exception as e:
        logger.error(f"任务提交失败: {e}")
        raise HTTPException(status_code=500, detail=f"任务提交失败: {str(e)}")


@router.get("/{task_id}/status", response_model=TaskResponse, summary="获取任务状态")
def get_task_status(task_id: str):
    """
    获取指定任务的状态信息
    
    - **task_id**: 任务ID
    """
    try:
        result = task_service.get_task_status(task_id)
        return result
        
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")


@router.get("", response_model=TaskListResponse, summary="获取任务列表")
def list_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    status: Optional[str] = Query(None, description="状态过滤")
):
    """
    获取任务列表，支持分页和状态过滤
    
    - **page**: 页码，从1开始
    - **page_size**: 每页大小，1-100
    - **status**: 状态过滤 (pending/running/success/failed/cancelled)
    """
    try:
        result = task_service.list_tasks(page=page, page_size=page_size, status=status)
        return result
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@router.delete("/{task_id}", summary="取消任务")
def cancel_task(task_id: str):
    """
    取消指定的任务
    
    - **task_id**: 任务ID
    """
    try:
        result = task_service.cancel_task(task_id)
        return result
        
    except Exception as e:
        logger.error(f"取消任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")


@router.post("/batch", response_model=BatchTaskResponse, summary="批量提交任务")
def submit_batch_tasks(request: BatchTaskRequest):
    """
    批量提交多个处理任务
    
    - **requests**: 任务请求列表，最多100个
    """
    try:
        results = []
        
        for req in request.requests:
            try:
                # 转换字幕数据
                subtitles_data = [sub.dict() for sub in req.subtitles]
                
                # 提交单个任务
                result = task_service.submit_task(
                    video_id=req.video_id,
                    subtitles=subtitles_data,
                    platform=req.platform,
                    task_type=req.task_type
                )
                
                results.append({
                    "video_id": req.video_id,
                    "status": "success",
                    "task_id": result["task_id"],
                    "message": "任务提交成功"
                })
                
            except Exception as e:
                results.append({
                    "video_id": req.video_id,
                    "status": "failed",
                    "error": str(e),
                    "message": "任务提交失败"
                })
        
        success_count = sum(1 for r in results if r["status"] == "success")
        
        return {
            "total": len(request.requests),
            "success": success_count,
            "failed": len(request.requests) - success_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"批量任务提交失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量任务提交失败: {str(e)}")


@router.get("/stats", response_model=TaskStatsResponse, summary="获取任务统计")
def get_task_stats():
    """
    获取任务统计信息
    
    返回任务状态分布、类型分布、工作进程数等统计信息
    """
    try:
        result = task_service.get_task_stats()
        return result
        
    except Exception as e:
        logger.error(f"获取任务统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务统计失败: {str(e)}")


@router.post("/sync", response_model=TaskResponse, summary="同步执行任务")
def execute_sync_task(request: TaskSubmitRequest):
    """
    同步执行任务（不使用Celery队列，直接返回结果）
    
    适用于简单的、快速的处理任务
    
    - **video_id**: 视频ID
    - **subtitles**: 字幕数据列表
    - **platform**: 平台类型
    - **task_type**: 任务类型 (detect/translate)
    """
    try:
        # 转换字幕数据
        subtitles_data = [sub.dict() for sub in request.subtitles]
        
        # 同步执行任务
        result = task_service.execute_sync_task(
            task_type=request.task_type,
            video_id=request.video_id,
            subtitles=subtitles_data,
            platform=request.platform
        )
        
        return result
        
    except Exception as e:
        logger.error(f"同步任务执行失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步任务执行失败: {str(e)}")
