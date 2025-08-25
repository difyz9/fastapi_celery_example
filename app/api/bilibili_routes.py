# app/api/bilibili_routes.py - Bilibili视频处理路由
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from app.models import BilibiliVideoCreate, TaskResponse
from app.services import TaskService
from app.services.bilibili_chain_service import BilibiliChainService

# 创建Bilibili任务路由器
router = APIRouter(prefix="/bilibili", tags=["Bilibili视频处理"])

# 服务实例
task_service = TaskService()
bilibili_chain_service = BilibiliChainService()

@router.post("/submit", response_model=TaskResponse)
async def submit_bilibili_task(
    request: BilibiliVideoCreate, 
    background_tasks: BackgroundTasks,
    chain_name: str = Query("video_processing_chain", description="处理链类型")
):
    """
    提交Bilibili视频处理任务 - 使用Celery Chain执行
    
    支持的任务链:
    - video_processing_chain: 完整视频处理 (字幕下载 -> 内容检查 -> 翻译 -> 语音合成 -> 上传COS)
    - subtitle_only_chain: 仅字幕处理 (下载 -> 检查 -> 翻译)  
    - speech_generation_chain: 语音生成 (翻译 -> 语音合成 -> 上传)
    """
    
    try:
        # 将Pydantic模型转换为字典
        video_data = request.dict()
        
        # 验证视频数据
        if not video_data.get("bvid"):
            raise ValueError("bvid是必需的")
        if not video_data.get("title"):
            raise ValueError("视频标题是必需的")
        
        # 提交Bilibili任务链
        result = task_service.submit_bilibili_task(
            video_data=video_data,
            chain_name=chain_name
        )
        
        # 添加后台任务监控Celery Chain状态
        # Chain的特点：按顺序执行，前一个任务的输出作为后一个任务的输入
        background_tasks.add_task(
            task_service.monitor_celery_task, 
            result["task_id"], 
            result["celery_result"]
        )
        
        return TaskResponse(
            task_id=result["task_id"],
            status="submitted",
            message=f"Bilibili视频处理任务链已提交: {result['description']}",
            request_data={
                "video_title": video_data.get("title"),
                "bvid": video_data.get("bvid"),
                "author": video_data.get("author"),
                "chain_name": chain_name,
                "chain_description": result["description"],
                "celery_task_id": result["celery_task_id"],
                "video_info": result.get("video_info", {}),
                "estimated_duration": "15-20秒" if chain_name == "video_processing_chain" else "8-12秒"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bilibili任务链提交失败: {str(e)}")

@router.get("/chains")
async def get_bilibili_chains():
    """获取可用的Bilibili处理链详情"""
    chains_info = {}
    
    for name, info in bilibili_chain_service.BILIBILI_CHAINS.items():
        chains_info[name] = {
            "description": info["description"],
            "tasks": info.get("tasks", []),
            "estimated_duration": {
                "video_processing_chain": "15-20秒",
                "subtitle_only_chain": "6-8秒", 
                "speech_generation_chain": "6-8秒"
            }.get(name, "未知"),
            "task_count": len(info.get("tasks", []))
        }
    
    return {
        "bilibili_chains": chains_info,
        "descriptions": {
            name: info["description"] 
            for name, info in bilibili_chain_service.BILIBILI_CHAINS.items()
        },
        "chain_execution_info": {
            "execution_mode": "Sequential Chain (顺序执行)",
            "data_flow": "每个任务的输出作为下一个任务的输入",
            "error_handling": "任何一步失败则整个链停止",
            "monitoring": "支持实时状态监控"
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

@router.get("/chain/{task_id}/progress")
async def get_chain_progress(task_id: str):
    """获取任务链执行进度"""
    try:
        # 获取任务状态
        task_status = task_service.get_task_status(task_id)
        
        # 根据任务状态判断执行进度
        if task_status["status"] == "pending":
            progress = {
                "status": "pending",
                "progress": 0,
                "current_step": "等待开始",
                "completed_steps": [],
                "estimated_remaining": "15-20秒"
            }
        elif task_status["status"] == "running":
            progress = {
                "status": "running", 
                "progress": 50,
                "current_step": "执行中",
                "completed_steps": ["已开始"],
                "estimated_remaining": "8-12秒"
            }
        elif task_status["status"] == "completed":
            # 分析结果确定完成了哪些步骤
            result = task_status.get("result", {})
            task_name = result.get("task_name", "")
            
            completed_steps = []
            progress_percent = 100
            
            if task_name == "upload_to_cos":
                completed_steps = [
                    "字幕下载", "内容检查", "字幕翻译", "语音生成", "文件上传"
                ]
                progress_percent = 100
            elif task_name == "generate_speech":
                completed_steps = ["字幕下载", "内容检查", "字幕翻译", "语音生成"]
                progress_percent = 80
            elif task_name == "translate_subtitle":
                completed_steps = ["字幕下载", "内容检查", "字幕翻译"]
                progress_percent = 60
            elif task_name == "check_subtitle_content":
                completed_steps = ["字幕下载", "内容检查"]
                progress_percent = 40
            elif task_name == "download_subtitle":
                completed_steps = ["字幕下载"]
                progress_percent = 20
            
            progress = {
                "status": "completed",
                "progress": progress_percent,
                "current_step": "已完成",
                "completed_steps": completed_steps,
                "final_result": result,
                "total_duration": "已完成"
            }
        else:  # failed
            progress = {
                "status": "failed",
                "progress": 0,
                "current_step": "执行失败",
                "completed_steps": [],
                "error": task_status.get("error")
            }
        
        return {
            "task_id": task_id,
            "chain_progress": progress,
            "task_details": task_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"任务不存在: {str(e)}")
