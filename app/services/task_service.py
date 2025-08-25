# app/services/task_service.py - 任务服务（使用ORM）
import uuid
from typing import Dict, Any
from app.database import ORMDatabaseManager
from app.services.chain_service import ChainService

class TaskService:
    """任务服务（基于ORM）"""
    
    def __init__(self, db_manager: ORMDatabaseManager = None):
        self.db_manager = db_manager or ORMDatabaseManager()
        self.chain_service = ChainService()
    
    def submit_task(self, a: int, b: int, operation_chain: str) -> Dict[str, Any]:
        """提交任务"""
        # 验证任务链
        if not self.chain_service.is_valid_chain(operation_chain):
            raise ValueError(f"不支持的任务链: {operation_chain}")
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务链
        task_chain = self.chain_service.create_chain(operation_chain, a, b)
        
        # 提交到Celery
        celery_result = task_chain.apply_async()
        celery_task_id = celery_result.id
        
        # 保存到数据库（使用ORM）
        task_record = self.db_manager.save_task_record(
            task_id=task_id,
            input_a=a,
            input_b=b,
            operation_chain=operation_chain,
            celery_task_id=celery_task_id
        )
        
        return {
            "task_id": task_id,
            "celery_result": celery_result,
            "celery_task_id": celery_task_id,
            "description": self.chain_service.get_chain_description(operation_chain),
            "task_record": task_record
        }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        task_record = self.db_manager.get_task_record(task_id)
        
        if not task_record:
            raise ValueError("任务不存在")
        
        return task_record.to_dict()
    
    def get_task_list(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """获取任务列表"""
        return self.db_manager.get_task_list(limit, offset)
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        # 检查任务是否存在
        task_record = self.db_manager.get_task_record(task_id)
        if not task_record:
            raise ValueError("任务不存在")
        
        return self.db_manager.delete_task(task_id)
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        return self.db_manager.get_task_statistics()
    
    def get_tasks_by_status(self, status: str, limit: int = 10) -> list:
        """根据状态获取任务列表"""
        tasks = self.db_manager.get_tasks_by_status(status, limit)
        return [task.to_dict() for task in tasks]
    
    def monitor_celery_task(self, task_id: str, celery_result):
        """监控Celery任务状态并更新数据库"""
        try:
            # 等待任务完成
            result = celery_result.get(timeout=60)  # 60秒超时
            
            # 更新数据库状态为成功
            self.db_manager.update_task_status(task_id, 'completed', result)
            print(f"✅ 任务 {task_id} 执行成功，结果: {result}")
            
        except Exception as e:
            # 更新数据库状态为失败
            self.db_manager.update_task_status(task_id, 'failed', error=str(e))
            print(f"❌ 任务 {task_id} 执行失败: {e}")
