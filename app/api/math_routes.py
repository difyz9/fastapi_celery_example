# app/api/math_routes.py - 数学任务路由
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models import MathRequest, TaskResponse
from app.services import TaskService
from app.services.math_chain_service import MathChainService

# 创建数学任务路由器
router = APIRouter(prefix="/math", tags=["数学任务"])

# 服务实例
task_service = TaskService()
math_chain_service = MathChainService()

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
    return {
        "math_chains": math_chain_service.get_available_chains(),
        "descriptions": {
            name: info["description"] 
            for name, info in math_chain_service.OPERATION_CHAINS.items()
        },
        "chain_execution_info": {
            "execution_mode": "Sequential Chain (顺序执行)",
            "supported_operations": ["加法", "乘法", "除法", "幂运算", "开方", "复数运算", "斐波那契", "二次方程"],
            "enhanced_features": ["错误处理", "状态跟踪", "结果验证"]
        }
    }
