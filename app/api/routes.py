# app/api/routes.py - API路由（使用ORM）
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from app.models import MathRequest, TaskResponse, TaskStatusResponse
from app.services import TaskService, ChainService
from app.database import ORMDatabaseManager

# 创建路由器
router = APIRouter()

# 服务实例（使用ORM数据库管理器）
task_service = TaskService()
chain_service = ChainService()

@router.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "数学运算任务链API",
        "version": "1.0.0",
        "architecture": "独立app层架构 + SQLAlchemy ORM",
        "available_chains": list(chain_service.OPERATION_CHAINS.keys()),
        "endpoints": {
            "submit_task": "/submit",
            "get_status": "/status/{task_id}",
            "list_tasks": "/tasks",
            "get_chains": "/chains",
            "get_statistics": "/statistics",
            "get_tasks_by_status": "/tasks/status/{status}"
        }
    }

@router.get("/chains")
async def get_available_chains():
    """获取可用的任务链"""
    return {
        "chains": chain_service.get_available_chains()
    }

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
            message=f"任务已提交，使用任务链: {result['description']}",
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

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    
    try:
        task_record = task_service.get_task_status(task_id)
        
        return TaskStatusResponse(
            task_id=task_record['id'],
            status=task_record['status'],
            input_data={
                "a": task_record['input_a'],
                "b": task_record['input_b'],
                "operation_chain": task_record['operation_chain']
            },
            result=task_record['result'],
            error=task_record['error_message'],
            created_at=task_record['created_at'],
            updated_at=task_record['updated_at']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")

@router.get("/tasks")
async def list_tasks(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    """获取任务列表"""
    
    try:
        return task_service.get_task_list(limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")

@router.get("/tasks/status/{status}")
async def get_tasks_by_status(status: str, limit: int = Query(10, ge=1, le=100)):
    """根据状态获取任务列表"""
    
    try:
        tasks = task_service.get_tasks_by_status(status, limit)
        return {
            "status": status,
            "count": len(tasks),
            "tasks": tasks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")

@router.get("/statistics")
async def get_task_statistics():
    """获取任务统计信息"""
    
    try:
        stats = task_service.get_task_statistics()
        return {
            "statistics": stats,
            "message": "任务统计信息"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务记录"""
    
    try:
        success = task_service.delete_task(task_id)
        if success:
            return {"message": f"任务 {task_id} 已删除"}
        else:
            raise HTTPException(status_code=500, detail="删除失败")
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")
