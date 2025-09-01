"""
任务模块初始化
"""

from .video_tasks import (
    process_video_subtitles,
    detect_language_only,
    TaskBuilder,
)

__all__ = [
    "process_video_subtitles",
    "detect_language_only",
    "TaskBuilder",
]
