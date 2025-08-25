# app/api/math_routes.py - 数学任务路由
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models import MathRequest, TaskResponse
from app.services import TaskService

# 创建数学任务路由器
router = APIRouter(prefix="/math", tags=["数学任务"])

# 服务实例
task_service = TaskService()

@router.post("/submit", response_model=TaskResponse)
async def submit_math_task(request: MathRequest, background_tasks: BackgroundTasks):
    """提交数学运算任务"""
    
    try:
        # 提交任务
        result = task_service.submit_task(
            a=request.a,
            b=request.b,
            operation_chain=request.operation_chain
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
            message=f"数学任务已提交，使用任务链: {result['description']}",
            request_data={
                "a": request.a,
                "b": request.b,
                "operation_chain": request.operation_chain,
                "celery_task_id": result["celery_task_id"]
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"任务提交失败: {str(e)}")

@router.get("/chains")
async def get_math_chains():
    """获取可用的数学运算链"""
    from app.services import ChainService
    return {
        "math_chains": ChainService.OPERATION_CHAINS,
        "descriptions": {
            name: info["description"] 
            for name, info in ChainService.OPERATION_CHAINS.items()
        }
    }
