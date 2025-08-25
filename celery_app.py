# celery_app.py - Celery应用配置和初始化
from celery import Celery
from config import CeleryConfig

# 创建全局应用实例
app = Celery('task_chain')

# 加载配置 - 直接设置配置
config_dict = CeleryConfig.get_config_dict()
for key, value in config_dict.items():
    setattr(app.conf, key, value)

# 立即导入所有任务模块
import tasks.math_tasks
import tasks.data_tasks  
import tasks.io_tasks

print(f"✅ 所有任务模块导入完成")
print(f"🔧 Broker: {app.conf.broker_url}")
print(f"🔧 Result Backend: {app.conf.result_backend}")
user_tasks = [t for t in app.tasks.keys() if not t.startswith('celery.')]
print(f"📋 已注册 {len(user_tasks)} 个用户任务")

if __name__ == '__main__':
    app.start()
