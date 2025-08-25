
# 🧮 数学运算任务链系统

一个基于Celery和FastAPI的分布式任务处理系统，采用现代化的app层架构和SQLAlchemy ORM，支持数学运算任务链的异步执行和Web界面管理。

## 🚀 核心特性

- **🏗️ 现代化架构**: 独立app层设计，分离API、服务、数据库和模型层
- **🗄️ ORM自动建表**: 基于SQLAlchemy的数据库模型，自动创建和管理表结构
- **⚡ 异步任务处理**: 基于Celery的分布式任务队列
- **📊 数学运算链**: 支持多种数学运算的组合执行
- **🌐 Web API接口**: RESTful API接口，支持任务提交和状态查询
- **💻 前端界面**: 用户友好的Web界面
- **💾 数据持久化**: SQLite数据库存储任务记录
- **📈 实时监控**: 任务状态实时更新和统计分析

## �️ 项目架构

### 新架构目录结构
```
task_chain/
├── 📄 readme.md              # 项目说明文档
├── 📦 requirements.txt       # Python依赖包
├── ⚙️ celery_app.py          # Celery应用配置
├── 🚀 server.py              # 新架构启动脚本
├── 🌐 web_server.py          # 前端Web服务器
├── 💻 web_interface.html     # Web前端界面
├── 🏗️ app/                   # 独立应用层
│   ├── 📄 main.py            # FastAPI主应用
│   ├── 🔌 api/               # API路由层
│   │   └── routes.py         # 路由定义
│   ├── 📊 models/            # 数据模型层
│   │   ├── request_models.py # 请求模型
│   │   ├── response_models.py# 响应模型
│   │   └── database_models.py# ORM数据库模型
│   ├── 🛠️ services/          # 业务服务层
│   │   ├── task_service.py   # 任务服务
│   │   └── chain_service.py  # 任务链服务
│   └── 🗄️ database/          # 数据库层
│       └── orm_database.py   # ORM数据库管理器
├── 📋 tasks/                 # 任务模块
│   ├── math_tasks.py         # 数学运算任务
│   ├── data_tasks.py         # 数据处理任务
│   └── io_tasks.py           # 输入输出任务
├── 🔄 workflows/             # 工作流模块
└── 🧪 tests/                 # 测试文件
    ├── test_api.py           # API测试
    ├── client_test.py        # 客户端测试
    └── curl_test.sh          # curl测试脚本
```

## 🛠️ 环境要求

- Python 3.12+
- Redis Server
- SQLAlchemy 2.0+ (ORM框架)
- 虚拟环境 (推荐)

## 📦 安装步骤

1. **创建并激活虚拟环境**
```bash
python3.12 -m venv venv
source venv/bin/activate  # macOS/Linux
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动Redis服务器**
```bash
# macOS (使用Homebrew)
brew services start redis

# 验证Redis运行
redis-cli ping
# 应该返回: PONG
```

## 🚀 启动服务

### 新架构启动方式

系统包含3个独立的服务，需要分别在不同的终端窗口中启动：

### 1. 启动Celery Worker (终端1)
```bash
# 确保在项目根目录并激活虚拟环境
cd /path/to/task_chain
source venv/bin/activate

# 启动Celery Worker
celery -A celery_app worker --loglevel=info

celery -A celery_app worker --loglevel=info --queues=celery,math,data,io,bilibili --concurrency=4


```

### 2. 启动FastAPI后端服务 (终端2)
```bash
# 确保在项目根目录并激活虚拟环境
cd /path/to/task_chain
source venv/bin/activate

# 启动新架构的API服务器
python server.py

# 或者使用uvicorn直接启动
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 启动前端Web服务器 (终端3)
```bash
# 确保在项目根目录并激活虚拟环境
cd /path/to/task_chain
source venv/bin/activate

# 启动前端服务器
python web_server.py
```

## 🌐 访问地址

启动成功后，可以通过以下地址访问：

- **前端界面**: http://localhost:3000
  - 提供Web界面进行任务管理和监控
  - 支持任务提交、状态查看、结果查询

- **后端API**: http://localhost:8000
  - FastAPI自动文档: http://localhost:8000/docs
  - 数据库自动初始化: 首次启动时自动创建所需表

## � API接口文档

### 核心功能接口

#### 1. 提交任务链
```bash
# POST /tasks/submit
curl -X POST "http://localhost:8000/tasks/submit" \
     -H "Content-Type: application/json" \
     -d '{
       "task_type": "data_chain",
       "description": "数据处理任务链",
       "config": {
         "data_input": "sample_data.csv",
         "processing_steps": ["clean", "transform", "analyze"]
       }
     }'
```

#### 2. 查询任务状态
```bash
# GET /tasks/{task_id}/status
curl "http://localhost:8000/tasks/abc123/status"

# 返回结果示例
{
  "task_id": "abc123",
  "status": "COMPLETED",
  "created_at": "2024-01-01T10:00:00",
  "completed_at": "2024-01-01T10:05:00",
  "result": {...}
}
```

#### 3. 获取任务结果
```bash
# GET /tasks/{task_id}/result
curl "http://localhost:8000/tasks/abc123/result"
```

#### 4. 获取系统统计信息
```bash
# GET /tasks/statistics
curl "http://localhost:8000/tasks/statistics"

# 返回结果示例
{
  "total_tasks": 150,
  "pending_tasks": 5,
  "running_tasks": 3,
  "completed_tasks": 140,
  "failed_tasks": 2
}
```

#### 5. 查询任务列表（支持状态过滤）
```bash
# GET /tasks?status=COMPLETED&limit=10
curl "http://localhost:8000/tasks?status=COMPLETED&limit=10"

# 查询所有任务
curl "http://localhost:8000/tasks"
```

#### 6. 删除任务
```bash
# DELETE /tasks/{task_id}
curl -X DELETE "http://localhost:8000/tasks/abc123"
```

### 支持的任务类型

| 任务类型 | 描述 | 配置参数 |
|---------|------|----------|
| `data_chain` | 数据处理任务链 | `data_input`, `processing_steps` |
| `math_chain` | 数学计算任务链 | `operation`, `numbers`, `iterations` |
| `io_chain` | IO操作任务链 | `file_operations`, `target_files` |

## 🧪 开发和测试

### 运行测试套件
```bash
# 运行API接口测试
python tests/test_api.py

# 运行客户端测试
python tests/client_test.py

# 使用curl脚本测试
chmod +x tests/curl_test.sh
./tests/curl_test.sh
```

### 开发调试
```bash
# 启动开发模式（热重载）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 查看详细日志
python server.py --log-level debug
```

## 📈 监控和管理

### Celery监控命令
```bash
# 查看活跃任务
celery -A celery_app inspect active

# 查看已注册任务
celery -A celery_app inspect registered

# 查看worker状态
celery -A celery_app status

# 查看worker统计信息
celery -A celery_app inspect stats
```

### 数据库管理
```bash
# 数据库表会在首次启动时自动创建
# 如需重置数据库，删除 tasks.db 文件后重启服务即可
rm tasks.db  # SQLite数据库文件
python server.py  # 重启服务自动重建表
```

## 🎯 架构优势

### 新架构特点
- **📊 ORM数据管理**: 使用SQLAlchemy自动处理数据库表创建和管理
- **🏗️ 分层架构**: API层、服务层、数据层清晰分离
- **🔧 易于扩展**: 模块化设计便于添加新功能
- **📈 性能优化**: 连接池、异步处理、错误重试机制
- **🛡️ 错误处理**: 完善的异常处理和状态管理

### 与旧架构对比
| 特性 | 旧架构 | 新架构 |
|------|--------|--------|
| 数据库 | 手写SQL | SQLAlchemy ORM |
| 配置管理 | 复杂配置类 | 直接conf.update() |
| API结构 | 单文件 | 分层模块化 |
| 错误处理 | 基础 | 完善的异常管理 |
| 可维护性 | 中等 | 高 |

## �️ 开发和测试

### 测试API功能
```bash
python test_api.py
```

### 运行主程序示例
```bash
python main.py
```

### 使用curl测试脚本
```bash
chmod +x curl_test.sh
./curl_test.sh
```

## 📈 监控和管理

### 查看Celery状态
```bash
## 🔧 配置说明

### 系统配置

#### Redis配置
- **主机**: localhost
- **端口**: 6379  
- **数据库**: 0
- **连接池**: 支持连接池管理

#### Celery配置
- **消息代理**: Redis (`redis://localhost:6379/0`)
- **结果后端**: Redis
- **任务序列化**: JSON
- **结果序列化**: JSON
- **任务超时**: 1800秒(30分钟)
- **重试机制**: 支持自动重试
- **预取策略**: 优化性能配置

#### 数据库配置
- **类型**: SQLite (可扩展至PostgreSQL/MySQL)
- **文件位置**: `./tasks.db`
- **ORM引擎**: SQLAlchemy 2.0+
- **自动初始化**: 启动时自动创建表结构

## 🚨 常见问题

### 启动问题

**Q: Redis连接失败**
```bash
# 确认Redis服务运行状态
brew services list | grep redis
redis-cli ping

# 如未安装Redis
brew install redis
brew services start redis
```

**Q: 端口占用冲突**
```bash
# 查看端口占用
lsof -i :8000  # API端口
lsof -i :3000  # Web端口

# 修改配置文件中的端口设置
```

**Q: 数据库权限问题**
```bash
# 确保项目目录有写权限
chmod 755 /path/to/task_chain
# SQLite文件会自动创建
```

### 性能优化

**任务执行缓慢**
- 增加Celery worker数量: `celery -A celery_app worker --concurrency=4`
- 调整Redis最大连接数
- 优化任务代码逻辑

**内存使用过高**
- 设置worker最大任务数: `--max-tasks-per-child=100`
- 定期清理完成的任务记录
- 使用任务结果过期设置

## � 相关资源

- [Celery官方文档](https://docs.celeryproject.org/)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [Redis文档](https://redis.io/documentation)

## 📝 更新日志

### v2.0 (当前版本)
- ✅ 全新app层架构设计
- ✅ SQLAlchemy ORM数据库管理
- ✅ 增强的API接口（统计、过滤、删除）
- ✅ 优化的Celery配置
- ✅ 完善的错误处理机制
- ✅ 分层服务架构

### v1.0 (历史版本)
- 基础Celery任务链功能
- 简单FastAPI接口
- 手写SQL数据管理
- 单文件架构设计

---

💡 **提示**: 如遇到问题，请先检查Redis服务状态和项目目录权限，大部分启动问题都与这两个因素相关。

## 🚨 故障排除

### 常见问题

1. **Redis连接失败**
   ```bash
   # 检查Redis是否运行
   redis-cli ping
   # 应该返回: PONG
   
   # 如果未运行，启动Redis
   brew services start redis
   ```

2. **任务执行失败**
   ```bash
   # 检查Celery worker日志
   celery -A celery_app worker --loglevel=debug
   ```

3. **API访问失败**
   ```bash
   # 检查FastAPI服务状态
   curl http://localhost:8000/
   ```

4. **前端跨域问题**
   - 使用 http://localhost:8080 访问前端
   - 不要直接打开HTML文件

### 启动检查清单

✅ Redis服务器运行中 (`redis-cli ping`)  
✅ 虚拟环境已激活  
✅ 所有依赖已安装 (`pip list`)  
✅ Celery Worker正常启动  
✅ FastAPI服务响应正常  
✅ 前端服务器运行中  

## 📊 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web前端界面    │    │   FastAPI后端   │    │  Celery Worker  │
│  (端口: 8080)   │◄──►│   (端口: 8000)  │◄──►│   (任务处理)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  SQLite数据库   │    │  Redis消息队列  │
                       │   (任务记录)    │    │   (任务分发)    │
                       └─────────────────┘    └─────────────────┘
```

## 🔮 扩展功能

### 添加新任务类型
1. 在 `tasks/` 目录创建新的任务模块
2. 使用 `@app.task` 装饰器定义任务
3. 在 `celery_app.py` 中导入新模块

### 添加新的运算链
1. 在 `math_tasks.py` 中定义新的链式任务
2. 在 `api.py` 中添加对应的路由
3. 在前端界面添加选项

## 📄 许可证

MIT License

## 👥 作者信息

- **版本**: 1.0.0
- **最后更新**: 2025年8月25日

---

**🎉 享受分布式任务处理的强大功能！**