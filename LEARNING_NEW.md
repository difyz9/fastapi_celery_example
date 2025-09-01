# FastAPI + Celery 学习案例

这是一个专门为学习 **FastAPI** 和 **Celery** 任务队列解耦设计的教学项目。

## 🎯 学习目标

1. **理解 FastAPI 与 Celery 的集成方式**
2. **掌握任务链（Task Chain）的设计模式**
3. **学习系统解耦的架构思想**
4. **了解异步任务处理的最佳实践**

## 📁 项目结构

```
fastapi_celery/
├── main.py                    # FastAPI 应用入口
├── requirements.txt           # 项目依赖
├── docker-compose.yml        # Docker 容器编排
├── .env                      # 环境变量配置
├── app/
│   ├── __init__.py
│   ├── core/                 # 核心组件
│   │   ├── processor.py      # 🔑 处理器核心模式
│   │   ├── celery_app.py     # Celery 配置
│   │   ├── config.py         # 配置管理
│   │   └── logger.py         # 日志配置
│   ├── processors/           # 具体处理器实现
│   │   ├── __init__.py
│   │   └── video_processors.py  # 视频处理器
│   ├── tasks/                # Celery 任务定义
│   │   ├── __init__.py
│   │   └── video_tasks.py    # 🔑 任务层
│   ├── api/                  # API 接口层
│   │   ├── __init__.py
│   │   ├── tasks.py          # 🔑 任务管理API
│   │   └── system.py         # 系统状态API
│   └── models/               # 数据模型
│       ├── __init__.py
│       └── task.py           # 任务相关模型
```

## 🏗️ 核心设计模式

### 1. 处理器模式 (Processor Pattern)

**位置**: `app/core/processor.py`

这是整个系统的核心设计，实现了**责任链模式**和**模板方法模式**：

```python
# 抽象基类定义了处理器的基本结构
class BaseProcessor:
    def execute(self, context: ProcessorContext) -> Dict[str, Any]:
        # 模板方法模式：定义执行流程
        start_time = time.time()
        try:
            result = self.process(context)  # 具体实现由子类提供
            execution_time = time.time() - start_time
            return self._build_success_result(result, execution_time)
        except Exception as e:
            execution_time = time.time() - start_time
            return self._build_error_result(str(e), execution_time)
    
    @abstractmethod
    def process(self, context: ProcessorContext) -> Dict[str, Any]:
        """子类必须实现的具体处理逻辑"""
        pass
```

**学习要点**：
- 每个处理器只负责一个明确的功能（单一责任原则）
- 处理器之间相互独立，可以灵活组合
- 统一的错误处理和执行时间统计

### 2. 处理器管道 (Processor Pipeline)

**位置**: `app/core/processor.py`

管道模式实现任务链的顺序执行：

```python
class ProcessorPipeline:
    def execute(self, context: ProcessorContext) -> Dict[str, Any]:
        for processor in self.processors:
            # 每个处理器的输出成为下一个处理器的输入
            result = processor.execute(context)
            if result["status"] != "success":
                break  # 遇到错误立即停止
            # 将结果合并到上下文中，传递给下一个处理器
            context.data.update(result.get("data", {}))
        return result
```

**学习要点**：
- 任务链的动态组合
- 错误传播机制
- 上下文数据的传递

### 3. 任务层解耦 (Task Layer Decoupling)

**位置**: `app/tasks/video_tasks.py`

Celery 任务层作为 API 和业务逻辑的中间层：

```python
@celery_app.task(bind=True, name="process_video_subtitles")
def process_video_subtitles(self, video_id: int, subtitles: list) -> Dict[str, Any]:
    # 1. 创建处理上下文
    context = ProcessorContext(video_id=video_id, data={"subtitles": subtitles})
    
    # 2. 组装处理器管道
    pipeline = ProcessorPipeline([
        LanguageDetectProcessor(),   # 语言检测
        TranslateProcessor(),        # 翻译
        AudioGenerateProcessor(),    # 音频生成
        UploadProcessor()            # 上传
    ])
    
    # 3. 执行任务链
    return pipeline.execute(context)
```

**学习要点**：
- API 层不直接处理业务逻辑
- 任务可以在后台异步执行
- 不同的任务可以组合不同的处理器

## 🔄 数据流程

```
HTTP请求 → FastAPI → Celery任务 → 处理器管道 → 具体处理器
    ↑                                                    ↓
   API响应 ← 任务状态查询 ← Redis结果存储 ← 处理结果返回
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动 Redis（作为消息代理）

```bash
# 使用 Docker
docker run -d -p 6379:6379 redis:latest

# 或使用 docker-compose
docker-compose up -d
```

### 3. 启动 Celery Worker

```bash
celery -A app.core.celery_app worker --loglevel=info
```

### 4. 启动 FastAPI 服务

```bash
uvicorn main:app --reload --port 8000
```

### 5. 测试 API

访问 http://localhost:8000/docs 查看 API 文档

提交任务：
```bash
curl -X POST "http://localhost:8000/api/tasks/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": 12345,
    "subtitles": [
      {"text": "Hello world", "start": 0.0, "end": 2.0},
      {"text": "这是一个测试", "start": 2.0, "end": 4.0}
    ]
  }'
```

查询任务状态：
```bash
curl "http://localhost:8000/api/tasks/status/{task_id}"
```

## 🎓 学习重点

### 1. 关键概念理解

- **解耦**: API层、任务层、处理器层各司其职
- **异步**: HTTP 请求立即返回，任务在后台执行
- **责任链**: 处理器可以灵活组合，形成不同的处理流程
- **错误处理**: 统一的错误传播和处理机制

### 2. 代码阅读顺序

1. `app/core/processor.py` - 理解核心设计模式
2. `app/processors/video_processors.py` - 看具体处理器实现
3. `app/tasks/video_tasks.py` - 理解任务层如何组装处理器
4. `app/api/tasks.py` - 学习 API 层如何调用任务
5. `main.py` - 看整个应用的启动流程

### 3. 扩展练习

1. **添加新处理器**: 实现一个新的处理器类
2. **创建新任务链**: 组合不同的处理器形成新的业务流程
3. **添加错误重试**: 在任务失败时自动重试
4. **实现任务优先级**: 不同类型的任务使用不同的队列

## 📚 相关技术

- **FastAPI**: 现代化的 Python Web 框架
- **Celery**: 分布式任务队列
- **Redis**: 内存数据库，用作消息代理
- **Pydantic**: 数据验证和序列化
- **设计模式**: 责任链模式、模板方法模式、管道模式

## 🤔 思考题

1. 如果要添加任务优先级，应该在哪一层实现？
2. 如何处理处理器之间的数据依赖关系？
3. 如果某个处理器执行时间很长，如何优化？
4. 如何实现任务的暂停和恢复功能？

这个项目展示了现代 Python 后端开发中的重要概念和最佳实践，是学习微服务架构和异步编程的很好的起点。
