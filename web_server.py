# web_server.py - 简单的Web服务器托管前端页面
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# 创建Web服务器应用
web_app = FastAPI(title="任务链前端", description="数学运算任务链前端界面")

# 托管静态文件
web_app.mount("/static", StaticFiles(directory="."), name="static")

@web_app.get("/")
async def read_index():
    """返回主页面"""
    return FileResponse('web_interface.html')

if __name__ == "__main__":
    print("🌐 启动前端Web服务器...")
    print("📄 前端页面: http://localhost:8080")
    print("🔗 API文档: http://localhost:8000/docs")
    uvicorn.run(web_app, host="0.0.0.0", port=8080)
