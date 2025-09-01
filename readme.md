# 视频处理任务系统

基于 FastAPI 和 Celery 的视频字幕处理任务管理系统。

## 功能特性

- ✨ **异步任务处理**: 基于 Celery 的分布式任务队列
- 🎯 **字幕处理链**: 语言检测 → 翻译 → 音频生成 → 上传
- 📊 **任务监控**: 实时任务状态跟踪和统计
- 🔄 **RESTful API**: 标准化的 API 接口设计
- 📝 **自动文档**: Swagger/OpenAPI 文档
- 🏥 **健康检查**: 系统组件状态监控
- 🧪 **测试覆盖**: 完整的单元测试

(base) apple@apple15 fastapi_celery % python3.12 -m venv venv
(base) apple@apple15 fastapi_celery % source venv/bin/activate


source venv/bin/activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000


source venv/bin/activate && celery -A app.core.celery_app worker --loglevel=info


source venv/bin/activate && python test_pipeline.py

## 项目结构

```
fastapi_celery/
├── app/                        # 应用程序主目录
│   ├── __init__.py
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   ├── tasks.py           # 任务管理API
│   │   └── system.py          # 系统API
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py          # 配置管理
│   │   ├── logger.py          # 日志配置
│   │   ├── celery_app.py      # Celery应用
│   │   └── processor.py       # 处理器基类
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic模型
├── processors
│   ├── README.md
│   ├── __init__.py
│   ├── audio_generate_processor.py
│   ├── language_detect_processor.py
│   ├── translate_processor.py
│   └── upload_processor.py
│   │   ├── __init__.py
│   │   └── task_service.py
│   └── tasks/                  # Celery任务
│       ├── __init__.py
│       └── video_tasks.py
├── tests/                      # 测试文件
│   ├── __init__.py
│   ├── test_api.py
│   └── test_processors.py
├── config/                     # 配置文件
├── main.py                     # 应用入口
├── requirements.txt            # 依赖包
├── .env.example               # 环境配置示例
├── start.sh                   # 启动脚本
└── README.md                  # 项目文档
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- Redis 服务器

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置（可选）
vim .env
```

### 4. 启动Redis

```bash
# macOS (使用 Homebrew)
brew services start redis

# Linux (使用 systemd)
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### 5. 启动服务

```bash
# 使用启动脚本（推荐）
chmod +x start.sh
./start.sh

# 或手动启动
# 1. 启动 Celery Worker
celery -A app.core.celery_app worker --loglevel=info

# 2. 启动 Celery Flower（可选）
celery -A app.core.celery_app flower --port=5555

# 3. 启动 FastAPI
python main.py




```

### 6. 访问服务

- **API文档**: http://localhost:8000/docs
- **Celery监控**: http://localhost:5555
- **健康检查**: http://localhost:8000/health
- **系统信息**: http://localhost:8000/info

## API 使用示例

### 提交任务

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/submit" \
     -H "Content-Type: application/json" \
     -d '{
       "video_id": 123456,
       "subtitles": [
         {
           "start_time": 0.0,
           "end_time": 5.5,
           "text": "欢迎观看这个视频",
           "language": "zh-CN"
         }
       ],
       "platform": "bilibili",
       "task_type": "full"
     }'
```

### 查询任务状态

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/{task_id}/status"
```

### 获取任务列表

```bash
curl -X GET "http://localhost:8000/api/v1/tasks?page=1&page_size=10"
```

### 同步执行任务

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/sync" \
     -H "Content-Type: application/json" \
     -d '{
       "video_id": 789012,
       "subtitles": [
         {
           "start_time": 0.0,
           "end_time": 3.0,
           "text": "Hello world",
           "language": "en"
         }
       ],
       "task_type": "detect"
     }'
```

## 任务类型

| 类型 | 描述 | 处理步骤 |
|------|------|----------|
| `detect` | 语言检测 | 字幕语言识别 |
| `translate` | 翻译 | 检测 → 翻译 |
| `full` | 完整处理 | 检测 → 翻译 → 音频生成 → 上传 |
| `audio_generate` | 音频生成 | 音频生成 → 上传 |

## 开发指南

### 添加新的处理器

1. 在 `app/processors/` 创建处理器类，继承 `BaseProcessor`
2. 实现 `process` 方法
3. 在 `__init__.py` 中导出

```python
from app.core.processor import BaseProcessor, ProcessorContext

class MyProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("我的处理器")
    
    def process(self, context: ProcessorContext) -> ProcessorContext:
        # 处理逻辑
        context.set("my_result", "处理完成")
        return context
```

### 添加新的任务

1. 在 `app/tasks/` 创建任务函数
2. 使用 `@celery_app.task` 装饰器
3. 在路由中调用

```python
@celery_app.task(bind=True)
def my_task(self, data):
    # 任务逻辑
    return {"status": "success", "data": data}
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api.py -v

# 运行测试并生成覆盖率报告
pytest --cov=app tests/
```

## 部署

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### 生产环境配置

```bash
# 设置环境变量
export DEBUG=false
export LOG_LEVEL=WARNING
export CELERY_BROKER_URL=redis://your-redis:6379/0

# 使用 gunicorn 启动
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 监控和日志

- 应用日志: `logs/app.log`
- Celery Worker日志: `logs/celery_worker.log`
- Celery Flower日志: `logs/celery_flower.log`

## 常见问题

### Q: Redis 连接失败
A: 确保 Redis 服务正在运行，检查连接配置

### Q: Celery Worker 无法启动
A: 检查 Python 路径和依赖安装

### Q: 任务执行失败
A: 查看 Celery Worker 日志和任务状态

## 贡献

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License
