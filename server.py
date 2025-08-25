# server.py - 新的服务器启动脚本
"""
独立的FastAPI服务器启动脚本
使用新的app层架构
"""

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    print("🚀 启动新架构的FastAPI服务器...")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔗 Redoc文档: http://localhost:8000/redoc")
    print("🏗️ 新架构: app层独立设计")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,  # 开发模式热重载
        log_level="info"
    )
