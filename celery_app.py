# celery_app.py - Celery应用配置和初始化
from celery import Celery
from config import CeleryConfig

# 创建全局应用实例
app = Celery('task_chain')

# 直接配置Celery - 更简洁直接的方式
app.conf.update(
    broker_url=CeleryConfig.BROKER_URL,
    result_backend=CeleryConfig.RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟
    task_soft_time_limit=25 * 60,  # 25分钟软限制
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
    # 任务路由配置
    task_routes={
        'tasks.math_tasks.*': {'queue': 'math'},
        'tasks.data_tasks.*': {'queue': 'data'},
        'tasks.io_tasks.*': {'queue': 'io'},
        'bilibili.*': {'queue': 'bilibili'},  # 修正Bilibili任务路由
        'add_multiply_divide': {'queue': 'math'},
        'power_sqrt': {'queue': 'math'},
        'complex_math': {'queue': 'math'},
    }
)

# 自动发现任务 - 使用包名而不是模块路径
app.autodiscover_tasks(['tasks'], force=True)

# 输出配置信息
print(f"✅ Celery应用启动完成")
print(f"🔧 Broker: {app.conf.broker_url}")
print(f"🔧 Result Backend: {app.conf.result_backend}")
print(f"⏰ 任务时间限制: {app.conf.task_time_limit}秒")
print(f"👷 Worker预取: {app.conf.worker_prefetch_multiplier}")

# 延迟获取任务列表（autodiscover需要时间）
def get_task_info():
    """获取任务信息"""
    user_tasks = [t for t in app.tasks.keys() if not t.startswith('celery.')]
    print(f"📋 已注册 {len(user_tasks)} 个用户任务")
    for task in sorted(user_tasks):
        print(f"   - {task}")

# 注册启动后回调
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """配置完成后的回调"""
    get_task_info()

if __name__ == '__main__':
    app.start()
