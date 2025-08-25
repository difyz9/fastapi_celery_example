# app/models/database_models.py - 数据库ORM模型
from sqlalchemy import Column, String, Integer, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from typing import Any, Optional

# 创建基类
Base = declarative_base()

class TaskRecord(Base):
    """任务记录模型"""
    __tablename__ = 'task_records'
    
    id = Column(String, primary_key=True, comment='任务ID')
    input_a = Column(Integer, nullable=False, comment='输入参数A')
    input_b = Column(Integer, nullable=False, comment='输入参数B')
    operation_chain = Column(String, nullable=False, comment='运算链类型')
    celery_task_id = Column(String, nullable=False, comment='Celery任务ID')
    status = Column(String, nullable=False, default='pending', comment='任务状态')
    result = Column(Text, nullable=True, comment='任务结果(JSON)')
    error_message = Column(Text, nullable=True, comment='错误信息')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'input_a': self.input_a,
            'input_b': self.input_b,
            'operation_chain': self.operation_chain,
            'celery_task_id': self.celery_task_id,
            'status': self.status,
            'result': json.loads(self.result) if self.result else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def set_result(self, result: Any):
        """设置任务结果"""
        self.result = json.dumps(result) if result is not None else None
    
    def get_result(self) -> Any:
        """获取任务结果"""
        return json.loads(self.result) if self.result else None
    
    def __repr__(self):
        return f"<TaskRecord(id='{self.id}', status='{self.status}', operation='{self.operation_chain}')>"
