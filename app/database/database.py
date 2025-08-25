# app/database/database.py - 数据库管理
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = 'tasks.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def save_task_record(self, task_id: str, input_a: int, input_b: int, 
                        operation_chain: str, celery_task_id: str):
        """保存任务记录到数据库"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO task_records 
                (id, input_a, input_b, operation_chain, celery_task_id, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (task_id, input_a, input_b, operation_chain, celery_task_id, 'pending', datetime.now()))
            conn.commit()
    
    def update_task_status(self, task_id: str, status: str, result: Any = None, error: str = None):
        """更新任务状态"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE task_records 
                SET status = ?, result = ?, error_message = ?, updated_at = ?
                WHERE id = ?
            ''', (status, json.dumps(result) if result else None, error, datetime.now(), task_id))
            conn.commit()
    
    def get_task_record(self, task_id: str) -> Optional[Dict]:
        """获取任务记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, input_a, input_b, operation_chain, celery_task_id, 
                       status, result, error_message, created_at, updated_at
                FROM task_records 
                WHERE id = ?
            ''', (task_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'input_a': row[1],
                    'input_b': row[2],
                    'operation_chain': row[3],
                    'celery_task_id': row[4],
                    'status': row[5],
                    'result': json.loads(row[6]) if row[6] else None,
                    'error_message': row[7],
                    'created_at': row[8],
                    'updated_at': row[9]
                }
        return None
    
    def get_task_list(self, limit: int = 10, offset: int = 0):
        """获取任务列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取总数
            cursor.execute('SELECT COUNT(*) FROM task_records')
            total = cursor.fetchone()[0]
            
            # 获取任务列表
            cursor.execute('''
                SELECT id, input_a, input_b, operation_chain, status, created_at, updated_at
                FROM task_records 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append({
                    'task_id': row[0],
                    'input_a': row[1],
                    'input_b': row[2],
                    'operation_chain': row[3],
                    'status': row[4],
                    'created_at': row[5],
                    'updated_at': row[6]
                })
            
            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "tasks": tasks
            }
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM task_records WHERE id = ?', (task_id,))
            conn.commit()
            return cursor.rowcount > 0

def init_database(db_path: str = 'tasks.db'):
    """初始化SQLite数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_records (
            id TEXT PRIMARY KEY,
            input_a INTEGER NOT NULL,
            input_b INTEGER NOT NULL,
            operation_chain TEXT NOT NULL,
            celery_task_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            result TEXT,
            error_message TEXT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")
