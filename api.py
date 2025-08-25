# api.py - FastAPI Web接口
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from celery_app import app as celery_app
from celery import chain
import sqlite3
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import json

# 初始化FastAPI应用
app = FastAPI(title="任务链API", description="数学运算任务链处理系统", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class MathRequest(BaseModel):
    a: int
    b: int
    operation_chain: Optional[str] = "add_multiply_divide"  # 默认任务链

# 响应模型
class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    request_data: Dict[str, Any]

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    input_data: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

# 数据库初始化
def init_database():
    """初始化SQLite数据库"""
    conn = sqlite3.connect('tasks.db')
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

# 数据库操作函数
def save_task_record(task_id: str, input_a: int, input_b: int, 
                    operation_chain: str, celery_task_id: str):
    """保存任务记录到数据库"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO task_records 
        (id, input_a, input_b, operation_chain, celery_task_id, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (task_id, input_a, input_b, operation_chain, celery_task_id, 'pending', datetime.now()))
    
    conn.commit()
    conn.close()

def update_task_status(task_id: str, status: str, result: Any = None, error: str = None):
    """更新任务状态"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE task_records 
        SET status = ?, result = ?, error_message = ?, updated_at = ?
        WHERE id = ?
    ''', (status, json.dumps(result) if result else None, error, datetime.now(), task_id))
    
    conn.commit()
    conn.close()

def get_task_record(task_id: str) -> Optional[Dict]:
    """获取任务记录"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, input_a, input_b, operation_chain, celery_task_id, 
               status, result, error_message, created_at, updated_at
        FROM task_records 
        WHERE id = ?
    ''', (task_id,))
    
    row = cursor.fetchone()
    conn.close()
    
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

# 任务链定义
OPERATION_CHAINS = {
    "add_multiply_divide": {
        "description": "加法 -> 乘法 -> 除法",
        "chain": lambda a, b: chain(
            celery_app.signature('math.add', args=[a, b]),      # a + b
            celery_app.signature('math.multiply', args=[2]),    # 结果 * 2
            celery_app.signature('math.divide', args=[3])       # 结果 / 3
        )
    },
    "power_sqrt": {
        "description": "幂运算 -> 开方",
        "chain": lambda a, b: chain(
            celery_app.signature('math.power', args=[a, b]),    # a ^ b
            celery_app.signature('math.sqrt')                   # √结果
        )
    },
    "complex_math": {
        "description": "复杂数学运算链",
        "chain": lambda a, b: chain(
            celery_app.signature('math.add', args=[a, b]),          # a + b
            celery_app.signature('math.multiply', args=[a]),        # 结果 * a
            celery_app.signature('math.subtract', args=[b]),        # 结果 - b
            celery_app.signature('math.divide', args=[2])           # 结果 / 2
        )
    }
}

# 后台任务：监控Celery任务状态并更新数据库
def monitor_celery_task(task_id: str, celery_result):
    """监控Celery任务状态并更新数据库"""
    try:
        # 等待任务完成
        result = celery_result.get(timeout=60)  # 60秒超时
        
        # 更新数据库状态为成功
        update_task_status(task_id, 'completed', result)
        print(f"✅ 任务 {task_id} 执行成功，结果: {result}")
        
    except Exception as e:
        # 更新数据库状态为失败
        update_task_status(task_id, 'failed', error=str(e))
        print(f"❌ 任务 {task_id} 执行失败: {e}")

# API端点
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_database()

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "数学运算任务链API",
        "version": "1.0.0",
        "available_chains": list(OPERATION_CHAINS.keys()),
        "endpoints": {
            "submit_task": "/submit",
            "get_status": "/status/{task_id}",
            "list_tasks": "/tasks"
        }
    }

@app.get("/chains")
async def get_available_chains():
    """获取可用的任务链"""
    return {
        "chains": {
            name: {"description": chain_info["description"]}
            for name, chain_info in OPERATION_CHAINS.items()
        }
    }

@app.post("/submit", response_model=TaskResponse)
async def submit_math_task(request: MathRequest, background_tasks: BackgroundTasks):
    """提交数学运算任务"""
    
    # 验证任务链类型
    if request.operation_chain not in OPERATION_CHAINS:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的任务链: {request.operation_chain}. 可用选项: {list(OPERATION_CHAINS.keys())}"
        )
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    try:
        # 创建任务链
        chain_info = OPERATION_CHAINS[request.operation_chain]
        task_chain = chain_info["chain"](request.a, request.b)
        
        # 提交任务到Celery
        celery_result = task_chain.apply_async()
        celery_task_id = celery_result.id
        
        # 保存到数据库
        save_task_record(
            task_id=task_id,
            input_a=request.a,
            input_b=request.b,
            operation_chain=request.operation_chain,
            celery_task_id=celery_task_id
        )
        
        # 添加后台任务监控Celery任务状态
        background_tasks.add_task(monitor_celery_task, task_id, celery_result)
        
        return TaskResponse(
            task_id=task_id,
            status="submitted",
            message=f"任务已提交，使用任务链: {chain_info['description']}",
            request_data={
                "a": request.a,
                "b": request.b,
                "operation_chain": request.operation_chain,
                "celery_task_id": celery_task_id
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"任务提交失败: {str(e)}")

@app.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    
    task_record = get_task_record(task_id)
    
    if not task_record:
        raise HTTPException(status_code=404, detail="任务不存在")
    
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

@app.get("/tasks")
async def list_tasks(limit: int = 10, offset: int = 0):
    """获取任务列表"""
    
    conn = sqlite3.connect('tasks.db')
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
    
    conn.close()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "tasks": tasks
    }

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务记录"""
    
    task_record = get_task_record(task_id)
    if not task_record:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM task_records WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    return {"message": f"任务 {task_id} 已删除"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动FastAPI服务器...")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔗 Redoc文档: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000)
