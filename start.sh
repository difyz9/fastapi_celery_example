#!/bin/bash

# FastAPI + Celery 启动脚本

echo "🚀 启动 FastAPI + Celery 视频处理服务"

# 检查Redis是否运行
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis 未运行，请先启动 Redis 服务"
    echo "   macOS: brew services start redis"
    echo "   Linux: sudo systemctl start redis"
    echo "   Docker: docker run -d -p 6379:6379 redis:alpine"
    exit 1
fi

echo "✅ Redis 服务正常"

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  建议在虚拟环境中运行"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
fi

# 创建日志目录
mkdir -p logs

# 创建环境配置文件（如果不存在）
if [ ! -f .env ]; then
    echo "📝 创建环境配置文件..."
    cp .env.example .env
    echo "✏️  请根据需要修改 .env 文件中的配置"
fi

# 启动Celery Worker (后台运行)
echo "🔄 启动 Celery Worker..."
celery -A app.core.celery_app worker --loglevel=info --logfile=logs/celery_worker.log --detach

# 启动Celery Flower (可选，用于监控)
echo "🌸 启动 Celery Flower 监控面板..."
celery -A app.core.celery_app flower --port=5555 --logfile=logs/celery_flower.log &

# 等待一下让Celery完全启动
sleep 3

echo "✅ Celery Worker 已启动"
echo "✅ Celery Flower 监控面板已启动 (http://localhost:5555)"

# 启动FastAPI应用
echo "🌐 启动 FastAPI 应用..."
echo "📋 API文档地址: http://localhost:8000/docs"
echo "🌸 Celery监控面板: http://localhost:5555"
echo "🏥 健康检查: http://localhost:8000/health"
echo "ℹ️  系统信息: http://localhost:8000/info"
echo "🔄 按 Ctrl+C 停止服务"

python main.py
