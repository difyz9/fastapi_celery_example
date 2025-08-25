# app/api/task_routes.py - 通用任务管理路由
from fastapi import APIRouter, HTTPException, Query
from app.models import TaskStatusResponse
from app.services import TaskService

# 创建任务管理路由器
router = APIRouter(prefix="/tasks", tags=["任务管理"])

# 服务实例
task_service = TaskService()

@router.get("/{task_id}/status", response_model=TaskStatusResponse)
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

@router.get("/{task_id}/result")
async def get_task_result(task_id: str):
    """获取任务结果"""
    
    try:
        task_record = task_service.get_task_status(task_id)
        
        if task_record['status'] != 'completed':
            return {
                "task_id": task_id,
                "status": task_record['status'],
                "message": "任务尚未完成",
                "result": None
            }
        
        return {
            "task_id": task_id,
            "status": task_record['status'],
            "result": task_record['result'],
            "created_at": task_record['created_at'],
            "completed_at": task_record['updated_at']
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务结果失败: {str(e)}")

@router.get("")
async def list_tasks(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    """获取任务列表"""
    
    try:
        return task_service.get_task_list(limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")

@router.get("/status/{status}")
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

@router.delete("/{task_id}")
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
