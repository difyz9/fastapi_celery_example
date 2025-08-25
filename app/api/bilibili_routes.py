# app/api/bilibili_routes.py - Bilibili视频处理路由
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from app.models import BilibiliVideoCreate, TaskResponse
from app.services import TaskService, ChainService

# 创建Bilibili任务路由器
router = APIRouter(prefix="/bilibili", tags=["Bilibili视频处理"])

# 服务实例
task_service = TaskService()
chain_service = ChainService()

@router.post("/submit", response_model=TaskResponse)
async def submit_bilibili_task(
    request: BilibiliVideoCreate, 
    background_tasks: BackgroundTasks,
    chain_name: str = Query("video_processing_chain", description="处理链类型")
):
    """提交Bilibili视频处理任务"""
    
    try:
        # 将Pydantic模型转换为字典
        video_data = request.dict()
        
        # 提交Bilibili任务
        result = task_service.submit_bilibili_task(
            video_data=video_data,
            chain_name=chain_name
        )
        
        # 添加后台任务监控Celery任务状态
        background_tasks.add_task(
            task_service.monitor_celery_task, 
            result["task_id"], 
            result["celery_result"]
        )
        
        return TaskResponse(
            task_id=result["task_id"],
            status="submitted",
            message=f"Bilibili视频处理任务已提交: {result['description']}",
            request_data={
                "video_title": video_data.get("title"),
                "bvid": video_data.get("bvid"),
                "author": video_data.get("author"),
                "chain_name": chain_name,
                "celery_task_id": result["celery_task_id"],
                "video_info": result.get("video_info", {})
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bilibili任务提交失败: {str(e)}")

@router.get("/chains")
async def get_bilibili_chains():
    """获取可用的Bilibili处理链"""
    return {
        "bilibili_chains": chain_service.BILIBILI_CHAINS,
        "descriptions": {
            name: info["description"] 
            for name, info in chain_service.BILIBILI_CHAINS.items()
        }
    }

@router.get("/video/{bvid}/info")
async def get_video_info(bvid: str):
    """获取视频信息（模拟接口）"""
    # 这里可以集成真实的Bilibili API
    return {
        "bvid": bvid,
        "title": "示例视频标题",
        "author": "示例UP主",
        "duration": 1800,
        "status": "available",
        "message": "这是一个模拟的视频信息接口"
    }
