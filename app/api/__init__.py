# app/api/__init__.py
from .routes import router
from . import math_routes, bilibili_routes, task_routes

__all__ = ["router", "math_routes", "bilibili_routes", "task_routes"]
