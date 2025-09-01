"""
任务管理服务
"""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.celery_app import celery_app
from app.core.logger import get_logger
from app.models.schemas import TaskType, TaskStatus, Platform
from app.tasks.video_tasks import (
    process_subtitles_task,
    detect_language_simple_task,
    translate_subtitles_task,
    generate_audio_task,
    TaskBuilder
)

logger = get_logger(__name__)


class TaskService:
    """任务管理服务类"""
    
    def __init__(self):
        # 内存存储（生产环境建议使用Redis或数据库）
        self.task_store: Dict[str, Dict[str, Any]] = {}
    
    def submit_task(self, video_id: int, subtitles: List[Dict], 
                   platform: str = "bilibili", task_type: str = "full") -> Dict[str, Any]:
        """
        提交处理任务
        
        Args:
            video_id: 视频ID
            subtitles: 字幕数据
            platform: 平台类型
            task_type: 任务类型
            
        Returns:
            Dict: 任务提交结果
        """
        try:
            # 转换字幕数据格式
            subtitles_data = [
                {
                    "start_time": sub.get("start_time", 0),
                    "end_time": sub.get("end_time", 0),
                    "text": sub.get("text", ""),
                    "language": sub.get("language")
                }
                for sub in subtitles
            ]
            
            # 根据任务类型选择不同的处理方式
            if task_type == TaskType.FULL:
                # 提交完整处理任务到Celery
                result = process_subtitles_task.delay(video_id, subtitles_data, platform)
                task_id = result.id
                
            elif task_type == TaskType.DETECT:
                # 提交语言检测任务
                result = detect_language_simple_task.delay(video_id, subtitles_data)
                task_id = result.id
                
            elif task_type == TaskType.TRANSLATE:
                # 提交翻译任务
                result = translate_subtitles_task.delay(video_id, subtitles_data, platform)
                task_id = result.id
                
            elif task_type == TaskType.AUDIO_GENERATE:
                # 提交音频生成任务
                result = generate_audio_task.delay(video_id, subtitles_data, platform)
                task_id = result.id
                
            else:
                raise ValueError(f"不支持的任务类型: {task_type}")
            
            # 保存任务信息
            self._save_task_info(task_id, video_id, task_type, TaskStatus.PENDING)
            
            return {
                "task_id": task_id,
                "status": TaskStatus.PENDING,
                "video_id": video_id,
                "task_type": task_type,
                "message": "任务已提交，正在处理中..."
            }
            
        except Exception as e:
            logger.error(f"任务提交失败: {e}")
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 任务状态信息
        """
        try:
            # 从Celery获取任务状态
            result = celery_app.AsyncResult(task_id)
            
            # 构建响应
            response = {
                "task_id": task_id,
                "status": result.status.lower(),
                "info": result.info if result.info else {}
            }
            
            # 如果任务完成，添加结果
            if result.successful():
                response["result"] = result.result
                response["status"] = TaskStatus.SUCCESS
            elif result.failed():
                response["status"] = TaskStatus.FAILED
                response["error"] = str(result.info) if result.info else "任务执行失败"
            elif result.state == "PENDING":
                response["status"] = TaskStatus.PENDING
            elif result.state == "STARTED":
                response["status"] = TaskStatus.RUNNING
            
            # 更新本地存储的任务状态
            if task_id in self.task_store:
                self._update_task_status(task_id, response["status"], response.get("result"))
                # 合并本地存储的信息
                local_info = self.task_store[task_id]
                response.update({
                    "video_id": local_info["video_id"],
                    "task_type": local_info.get("task_type", "unknown"),
                    "created_at": local_info["created_at"],
                    "updated_at": local_info["updated_at"]
                })
            
            return response
            
        except Exception as e:
            logger.error(f"获取任务状态失败: {e}")
            raise
    
    def list_tasks(self, page: int = 1, page_size: int = 10, 
                  status: Optional[str] = None) -> Dict[str, Any]:
        """
        获取任务列表
        
        Args:
            page: 页码
            page_size: 每页大小
            status: 状态过滤
            
        Returns:
            Dict: 任务列表
        """
        try:
            # 过滤任务
            filtered_tasks = list(self.task_store.values())
            if status:
                filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
            
            # 排序（按创建时间倒序）
            filtered_tasks.sort(key=lambda x: x["created_at"], reverse=True)
            
            # 分页
            total = len(filtered_tasks)
            start = (page - 1) * page_size
            end = start + page_size
            tasks = filtered_tasks[start:end]
            
            return {
                "tasks": tasks,
                "total": total,
                "page": page,
                "page_size": page_size,
                "has_next": end < total,
                "has_prev": page > 1
            }
            
        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            raise
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 取消结果
        """
        try:
            # 撤销Celery任务
            celery_app.control.revoke(task_id, terminate=True)
            
            # 更新本地状态
            if task_id in self.task_store:
                self._update_task_status(task_id, TaskStatus.CANCELLED)
            
            return {
                "task_id": task_id,
                "status": TaskStatus.CANCELLED,
                "message": "任务已取消"
            }
            
        except Exception as e:
            logger.error(f"取消任务失败: {e}")
            raise
    
    def get_task_stats(self) -> Dict[str, Any]:
        """
        获取任务统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            from collections import Counter
            
            # 统计任务状态
            status_counts = Counter(task["status"] for task in self.task_store.values())
            
            # 统计任务类型
            type_counts = Counter(task.get("task_type", "unknown") for task in self.task_store.values())
            
            # 获取Celery工作进程信息
            inspect = celery_app.control.inspect()
            active_workers = inspect.active() or {}
            active_queues = inspect.active_queues() or {}
            
            return {
                "total_tasks": len(self.task_store),
                "status_distribution": dict(status_counts),
                "type_distribution": dict(type_counts),
                "celery_workers": len(active_workers),
                "active_tasks": sum(len(tasks) for tasks in active_workers.values())
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            raise
    
    def execute_sync_task(self, task_type: str, video_id: int, 
                         subtitles: List[Dict], platform: str = "bilibili") -> Dict[str, Any]:
        """
        同步执行任务（不使用Celery队列）
        
        Args:
            task_type: 任务类型
            video_id: 视频ID
            subtitles: 字幕数据
            platform: 平台类型
            
        Returns:
            Dict: 任务执行结果
        """
        try:
            task_id = str(uuid.uuid4())
            
            # 转换字幕数据格式
            subtitles_data = [
                {
                    "start_time": sub.get("start_time", 0),
                    "end_time": sub.get("end_time", 0),
                    "text": sub.get("text", ""),
                    "language": sub.get("language")
                }
                for sub in subtitles
            ]
            
            # 根据任务类型执行不同的处理
            if task_type == TaskType.DETECT:
                result = TaskBuilder.subtitle_detection_only(video_id, subtitles_data)
            elif task_type == TaskType.TRANSLATE:
                result = TaskBuilder.translation_pipeline(video_id, subtitles_data, platform)
            elif task_type == TaskType.FULL:
                result = TaskBuilder.full_pipeline(video_id, subtitles_data, platform)
            else:
                raise ValueError(f"不支持的同步任务类型: {task_type}")
            
            # 保存任务信息
            self._save_task_info(task_id, video_id, task_type, TaskStatus.SUCCESS)
            self._update_task_status(task_id, TaskStatus.SUCCESS, result)
            
            return {
                "task_id": task_id,
                "status": TaskStatus.SUCCESS,
                "video_id": video_id,
                "task_type": task_type,
                "result": result,
                "message": f"{task_type}任务同步执行完成"
            }
            
        except Exception as e:
            logger.error(f"同步任务执行失败: {e}")
            raise
    
    def _save_task_info(self, task_id: str, video_id: int, task_type: str, status: str):
        """保存任务信息"""
        self.task_store[task_id] = {
            "task_id": task_id,
            "video_id": video_id,
            "task_type": task_type,
            "status": status,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "result": None
        }
    
    def _update_task_status(self, task_id: str, status: str, result: Dict[str, Any] = None):
        """更新任务状态"""
        if task_id in self.task_store:
            self.task_store[task_id]["status"] = status
            self.task_store[task_id]["updated_at"] = datetime.now()
            if result:
                self.task_store[task_id]["result"] = result


# 创建全局任务服务实例
task_service = TaskService()
