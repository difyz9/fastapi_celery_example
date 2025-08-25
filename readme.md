
# 🧮 数学运算任务链系统

一个基于Celery和FastAPI的分布式任务处理系统，支持数学运算任务链的异步执行和Web界面管理。

## 🚀 核心特性

- **异步任务处理**: 基于Celery的分布式任务队列
- **数学运算链**: 支持多种数学运算的组合执行
- **Web API接口**: RESTful API接口，支持任务提交和状态查询
- **前端界面**: 用户友好的Web界面
- **数据持久化**: SQLite数据库存储任务记录
- **实时监控**: 任务状态实时更新
- **标准化架构**: 模块化设计，易于扩展

## 📁 项目结构

```
task_chain/
├── readme.md              # 项目说明文档
├── requirements.txt       # Python依赖包
├── celery_app.py          # Celery应用配置
├── api.py                 # FastAPI后端服务
├── web_server.py          # 前端Web服务器
├── web_interface.html     # Web前端界面
├── main.py                # 主程序示例
├── tasks/                 # 任务模块
│   ├── __init__.py
│   ├── math_tasks.py      # 数学运算任务
│   ├── data_tasks.py      # 数据处理任务
│   └── io_tasks.py        # 输入输出任务
├── workflows/             # 工作流模块
│   ├── __init__.py
│   └── data_workflow.py   # 数据工作流
└── tests/                 # 测试文件
    ├── test_api.py        # API测试
    ├── client_test.py     # 客户端测试
    └── curl_test.sh       # curl测试脚本
```

## 🛠️ 环境要求

- Python 3.12+
- Redis Server
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

系统包含3个独立的服务，需要分别在不同的终端窗口中启动：

### 1. 启动Celery Worker (终端1)
```bash
# 确保在项目根目录并激活虚拟环境
cd /path/to/task_chain
source venv/bin/activate

# 启动Celery Worker
celery -A celery_app worker --loglevel=info
```

### 2. 启动FastAPI后端服务 (终端2)
```bash
# 确保在项目根目录并激活虚拟环境
cd /path/to/task_chain
source venv/bin/activate

# 启动API服务器
python api.py
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

启动所有服务后，可以通过以下地址访问：

- **🖥️ Web前端界面**: http://localhost:8080
- **📚 API文档**: http://localhost:8000/docs
- **🔧 API基础地址**: http://localhost:8000

## 📊 支持的数学运算链

### 1. 加法→乘法→除法 (`add_multiply_divide`)
```
输入: a=10, b=5
流程: (10 + 5) → 15 × 2 → 30 ÷ 3 = 10.0
```

### 2. 幂运算→开方 (`power_sqrt`)
```
输入: a=3, b=4
流程: 3^4 → √81 = 9.0
```

### 3. 复杂数学运算 (`complex_math`)
```
输入: a=20, b=8
流程: (20 + 8) → 28 × 20 → 560 - 8 → 552 ÷ 2 = 276.0
```

## 🔌 API使用示例

### 提交任务
```bash
curl -X POST "http://localhost:8000/submit" 
  -H "Content-Type: application/json" 
  -d '{
    "a": 10,
    "b": 5,
    "operation_chain": "add_multiply_divide"
  }'
```

### 查询任务状态
```bash
curl -X GET "http://localhost:8000/status/{task_id}"
```

### 获取任务列表
```bash
curl -X GET "http://localhost:8000/tasks?limit=10"
```

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
# 查看活跃任务
celery -A celery_app inspect active

# 查看已注册任务
celery -A celery_app inspect registered

# 查看worker状态
celery -A celery_app status

# 查看统计信息
celery -A celery_app inspect stats
```

### 数据库管理
- **数据库文件**: `tasks.db` (SQLite)
- **任务记录表**: `task_records`
- **自动创建**: 首次运行时自动创建数据库和表

## 🔧 配置说明

### Redis配置
默认连接配置：
- 主机: localhost
- 端口: 6379
- 数据库: 0

### Celery配置
- **消息代理**: Redis
- **结果后端**: Redis
- **任务序列化**: JSON
- **结果序列化**: JSON

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