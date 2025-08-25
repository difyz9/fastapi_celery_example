# tasks/base.py - 任务基类
from celery.utils.log import get_task_logger
from typing import Any, Callable
from functools import wraps
import time

class BaseTask:
    """任务基类，提供通用功能"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_task_logger(name)
    
    def log_start(self, *args, **kwargs):
        """记录任务开始"""
        self.logger.info(f"开始执行任务 {self.name}, 参数: args={args}, kwargs={kwargs}")
    
    def log_success(self, result: Any):
        """记录任务成功"""
        self.logger.info(f"任务 {self.name} 执行成功, 结果: {result}")
    
    def log_error(self, error: Exception):
        """记录任务错误"""
        self.logger.error(f"任务 {self.name} 执行失败: {str(error)}")

def task_wrapper(name: str = None, bind: bool = False, **task_kwargs):
    """任务装饰器，提供标准化的任务包装"""
    
    def decorator(func: Callable) -> Callable:
        task_name = name or f"{func.__module__}.{func.__name__}"
        base_task = BaseTask(task_name)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # 记录开始
                base_task.log_start(*args, **kwargs)
                
                # 执行任务
                result = func(*args, **kwargs)
                
                # 记录成功
                execution_time = time.time() - start_time
                base_task.logger.info(f"任务执行耗时: {execution_time:.2f}秒")
                base_task.log_success(result)
                
                return result
                
            except Exception as e:
                # 记录错误
                base_task.log_error(e)
                raise
        
        # 延迟获取app实例并注册任务
        def get_task():
            from celery_app import app
            return app.task(
                name=task_name,
                bind=bind,
                **task_kwargs
            )(wrapper)
        
        # 返回包装后的函数，并添加任务注册方法
        wrapped_func = wrapper
        wrapped_func._get_task = get_task
        wrapped_func._task_name = task_name
        
        return wrapped_func
    
    return decorator
