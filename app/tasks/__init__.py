"""
任务模块初始化
"""

from .video_tasks import (
    process_subtitles_task,
    detect_language_simple_task,
    translate_subtitles_task,
    generate_audio_task,
    TaskBuilder,
)

__all__ = [
    "process_subtitles_task",
    "detect_language_simple_task",
    "translate_subtitles_task", 
    "generate_audio_task",
    "TaskBuilder",
]
