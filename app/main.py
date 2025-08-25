# app/main.py - FastAPI主应用（使用ORM自动建表）
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.database import ORMDatabaseManager

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    
    # 创建应用实例
    app = FastAPI(
        title="数学运算任务链API",
        description="基于Celery的分布式任务处理系统 - 独立app层架构 + SQLAlchemy ORM",
        version="1.0.0",
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
    
    # 注册路由
    app.include_router(router)
    
    # 启动事件
    @app.on_event("startup")
    async def startup_event():
        """应用启动时自动初始化数据库"""
        # ORM数据库管理器会在初始化时自动创建表
        db_manager = ORMDatabaseManager()
        print("🚀 FastAPI应用启动完成（ORM自动建表）")
        print("📊 数据库表已根据模型自动创建")
    
    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动FastAPI服务器...")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔗 Redoc文档: http://localhost:8000/redoc")
    print("🏗️ 架构: 独立app层 + SQLAlchemy ORM")
    uvicorn.run(app, host="0.0.0.0", port=8000)
