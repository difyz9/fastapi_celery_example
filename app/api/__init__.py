"""
API模块初始化
"""

from .tasks import router as tasks_router
from .system import router as system_router

__all__ = [
    "tasks_router",
    "system_router",
]
