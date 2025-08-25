# app/main.py - FastAPI主应用（使用ORM自动建表）
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.api import math_routes, bilibili_routes, task_routes
from app.database import ORMDatabaseManager

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    
    # 创建应用实例
    app = FastAPI(
        title="任务链处理API",
        description="基于Celery的分布式任务处理系统 - 支持数学运算和Bilibili视频处理",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 在生产环境中应该设置具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册主路由（系统信息）
    app.include_router(router)
    
    # 注册功能模块路由
    app.include_router(math_routes.router)        # 数学任务路由
    app.include_router(bilibili_routes.router)    # Bilibili任务路由  
    app.include_router(task_routes.router)        # 通用任务管理路由
    
    # 启动事件
    @app.on_event("startup")
    async def startup_event():
        """应用启动时自动初始化数据库"""
        # ORM数据库管理器会在初始化时自动创建表
        db_manager = ORMDatabaseManager()
        print("🚀 FastAPI应用启动完成（模块化路由架构）")
        print("📊 数据库表已根据模型自动创建")
        print("🔧 路由模块: math, bilibili, tasks")
    
    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动FastAPI服务器...")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔗 Redoc文档: http://localhost:8000/redoc")
    print("🏗️架构: 独立app层 + SQLAlchemy ORM + 模块化路由")
    uvicorn.run(app, host="0.0.0.0", port=8000)
