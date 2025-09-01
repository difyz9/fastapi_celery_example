"""
FastAPI + Celery 学习案例 - 主应用
展示任务链和解耦设计的核心概念
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.core.logger import setup_logging, get_logger
from app.api import tasks_router, system_router

# 初始化日志
setup_logging()
logger = get_logger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="任务链学习案例",
    description="FastAPI + Celery 任务链和解耦设计示例",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置 - 允许前端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 学习环境，生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(system_router)  # 系统信息和健康检查
app.include_router(tasks_router, prefix="/api/v1")  # 任务管理API

@app.get("/")
def read_root():
    """欢迎页面 - 学习入口"""
    return {
        "message": "🎓 FastAPI + Celery 任务链学习案例",
        "learning_guide": "/docs",  # API 文档
        "health_check": "/health",  # 健康检查
        "system_info": "/info",     # 系统信息
        "celery_monitor": "http://localhost:5555",  # Celery 监控
        "key_concepts": {
            "task_chain": "将复杂任务分解为多个独立步骤",
            "decoupling": "通过处理器模式实现解耦",
            "async_queue": "使用 Celery 实现异步任务处理"
        }
    }

if __name__ == "__main__":
    logger.info("🚀 启动学习案例服务")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式自动重载
        log_level="info"
    )


