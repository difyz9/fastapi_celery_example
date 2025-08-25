# tasks/__init__.py
# 导入所有任务模块以便Celery能够发现它们
from . import math_tasks
from . import data_tasks  
from . import io_tasks