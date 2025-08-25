# app/database/orm_database.py - 基于SQLAlchemy的数据库管理
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from app.models.database_models import Base, TaskRecord

class ORMDatabaseManager:
    """基于SQLAlchemy ORM的数据库管理器"""
    
    def __init__(self, database_url: str = "sqlite:///tasks.db"):
        """
        初始化数据库管理器
        
        Args:
            database_url: 数据库连接URL
        """
        self.engine = create_engine(
            database_url,
            echo=False,  # 设置为True可以看到SQL语句
            pool_pre_ping=True,  # 连接池预ping检查
        )
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # 创建所有表
        self.create_tables()
    
    def create_tables(self):
        """创建所有数据库表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            print("✅ 数据库表创建完成（基于ORM模型）")
        except Exception as e:
            print(f"❌ 创建数据库表失败: {e}")
            raise
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    def save_task_record(self, task_id: str, input_a: int, input_b: int, 
                        operation_chain: str, celery_task_id: str) -> TaskRecord:
        """保存任务记录到数据库"""
        with self.get_session() as session:
            try:
                task_record = TaskRecord(
                    id=task_id,
                    input_a=input_a,
                    input_b=input_b,
                    operation_chain=operation_chain,
                    celery_task_id=celery_task_id,
                    status='pending',
                    created_at=datetime.now()
                )
                
                session.add(task_record)
                session.commit()
                session.refresh(task_record)
                
                print(f"✅ 任务记录已保存: {task_id}")
                return task_record
                
            except SQLAlchemyError as e:
                session.rollback()
                print(f"❌ 保存任务记录失败: {e}")
                raise
    
    def update_task_status(self, task_id: str, status: str, 
                          result: Any = None, error: str = None) -> Optional[TaskRecord]:
        """更新任务状态"""
        with self.get_session() as session:
            try:
                task_record = session.query(TaskRecord).filter(
                    TaskRecord.id == task_id
                ).first()
                
                if not task_record:
                    print(f"⚠️ 任务记录不存在: {task_id}")
                    return None
                
                task_record.status = status
                task_record.updated_at = datetime.now()
                
                if result is not None:
                    task_record.set_result(result)
                
                if error:
                    task_record.error_message = error
                
                session.commit()
                session.refresh(task_record)
                
                print(f"✅ 任务状态已更新: {task_id} -> {status}")
                return task_record
                
            except SQLAlchemyError as e:
                session.rollback()
                print(f"❌ 更新任务状态失败: {e}")
                raise
    
    def get_task_record(self, task_id: str) -> Optional[TaskRecord]:
        """获取任务记录"""
        with self.get_session() as session:
            try:
                task_record = session.query(TaskRecord).filter(
                    TaskRecord.id == task_id
                ).first()
                
                if task_record:
                    # 分离对象，避免会话关闭后无法访问
                    session.expunge(task_record)
                
                return task_record
                
            except SQLAlchemyError as e:
                print(f"❌ 获取任务记录失败: {e}")
                raise
    
    def get_task_list(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """获取任务列表"""
        with self.get_session() as session:
            try:
                # 获取总数
                total = session.query(TaskRecord).count()
                
                # 获取任务列表
                tasks_query = session.query(TaskRecord)\
                    .order_by(TaskRecord.created_at.desc())\
                    .limit(limit)\
                    .offset(offset)
                
                tasks = []
                for task in tasks_query:
                    task_dict = {
                        'task_id': task.id,
                        'input_a': task.input_a,
                        'input_b': task.input_b,
                        'operation_chain': task.operation_chain,
                        'status': task.status,
                        'created_at': task.created_at.isoformat() if task.created_at else None,
                        'updated_at': task.updated_at.isoformat() if task.updated_at else None
                    }
                    tasks.append(task_dict)
                
                return {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "tasks": tasks
                }
                
            except SQLAlchemyError as e:
                print(f"❌ 获取任务列表失败: {e}")
                raise
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务记录"""
        with self.get_session() as session:
            try:
                task_record = session.query(TaskRecord).filter(
                    TaskRecord.id == task_id
                ).first()
                
                if not task_record:
                    return False
                
                session.delete(task_record)
                session.commit()
                
                print(f"✅ 任务记录已删除: {task_id}")
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                print(f"❌ 删除任务记录失败: {e}")
                raise
    
    def get_tasks_by_status(self, status: str, limit: int = 10) -> List[TaskRecord]:
        """根据状态获取任务列表"""
        with self.get_session() as session:
            try:
                tasks = session.query(TaskRecord)\
                    .filter(TaskRecord.status == status)\
                    .order_by(TaskRecord.created_at.desc())\
                    .limit(limit)\
                    .all()
                
                # 分离对象
                for task in tasks:
                    session.expunge(task)
                
                return tasks
                
            except SQLAlchemyError as e:
                print(f"❌ 根据状态获取任务失败: {e}")
                raise
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        with self.get_session() as session:
            try:
                total_tasks = session.query(TaskRecord).count()
                pending_tasks = session.query(TaskRecord)\
                    .filter(TaskRecord.status == 'pending').count()
                completed_tasks = session.query(TaskRecord)\
                    .filter(TaskRecord.status == 'completed').count()
                failed_tasks = session.query(TaskRecord)\
                    .filter(TaskRecord.status == 'failed').count()
                
                return {
                    "total": total_tasks,
                    "pending": pending_tasks,
                    "completed": completed_tasks,
                    "failed": failed_tasks,
                    "success_rate": round(completed_tasks / total_tasks * 100, 2) if total_tasks > 0 else 0
                }
                
            except SQLAlchemyError as e:
                print(f"❌ 获取任务统计失败: {e}")
                raise
