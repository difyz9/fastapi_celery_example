"""
Pydantic数据模型
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    """任务类型枚举"""
    FULL = "full"
    DETECT = "detect"
    TRANSLATE = "translate"
    AUDIO_GENERATE = "audio_generate"
    AUDIO_UPLOAD = "audio_upload"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Platform(str, Enum):
    """平台类型枚举"""
    BILIBILI = "bilibili"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"


class SubtitleData(BaseModel):
    """字幕数据模型"""
    start_time: float = Field(description="开始时间(秒)", ge=0)
    end_time: float = Field(description="结束时间(秒)", ge=0)
    text: str = Field(description="字幕文本", min_length=1)
    language: Optional[str] = Field(None, description="语言代码")

    class Config:
        json_schema_extra = {
            "example": {
                "start_time": 0.0,
                "end_time": 5.5,
                "text": "Hello world",
                "language": "en"
            }
        }


class VideoInfo(BaseModel):
    """视频信息模型"""
    video_id: str = Field(description="视频ID")
    title: str = Field(description="视频标题")
    platform: Platform = Field(description="平台类型")
    duration: Optional[float] = Field(None, description="视频时长(秒)")
    author: Optional[str] = Field(None, description="作者")
    url: Optional[str] = Field(None, description="视频链接")
    description: Optional[str] = Field(None, description="视频描述")

    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "BV1234567890",
                "title": "示例视频",
                "platform": "bilibili",
                "duration": 300.0,
                "author": "示例作者",
                "url": "https://bilibili.com/video/BV1234567890",
                "description": "这是一个示例视频"
            }
        }


class TaskSubmitRequest(BaseModel):
    """任务提交请求模型"""
    video_id: int = Field(description="视频ID", gt=0)
    subtitles: List[SubtitleData] = Field(description="字幕数据列表", min_items=1)
    platform: Platform = Field(default=Platform.BILIBILI, description="平台类型")
    task_type: TaskType = Field(default=TaskType.FULL, description="任务类型")
    video_info: Optional[VideoInfo] = Field(None, description="视频信息")

    class Config:
        json_schema_extra = {
            "example": {
                "video_id": 123456,
                "subtitles": [
                    {
                        "start_time": 0.0,
                        "end_time": 5.5,
                        "text": "欢迎观看这个视频",
                        "language": "zh-CN"
                    }
                ],
                "platform": "bilibili",
                "task_type": "full"
            }
        }


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str = Field(description="任务ID")
    status: str = Field(description="任务状态")
    video_id: int = Field(description="视频ID")
    task_type: TaskType = Field(description="任务类型")
    message: str = Field(description="状态消息")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid-1234",
                "status": "success",
                "video_id": 123456,
                "task_type": "full",
                "message": "任务已完成",
                "result": {"processed_count": 10},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:05:00Z"
            }
        }


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    tasks: List[TaskResponse] = Field(description="任务列表")
    total: int = Field(description="总数", ge=0)
    page: int = Field(description="页码", ge=1)
    page_size: int = Field(description="每页大小", ge=1)
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")


class BatchTaskRequest(BaseModel):
    """批量任务请求模型"""
    requests: List[TaskSubmitRequest] = Field(description="任务请求列表", min_items=1, max_items=100)

    class Config:
        json_schema_extra = {
            "example": {
                "requests": [
                    {
                        "video_id": 123456,
                        "subtitles": [
                            {
                                "start_time": 0.0,
                                "end_time": 5.5,
                                "text": "视频1的字幕",
                                "language": "zh-CN"
                            }
                        ],
                        "platform": "bilibili",
                        "task_type": "full"
                    }
                ]
            }
        }


class BatchTaskResponse(BaseModel):
    """批量任务响应模型"""
    total: int = Field(description="总任务数")
    success: int = Field(description="成功提交数")
    failed: int = Field(description="失败数")
    results: List[Dict[str, Any]] = Field(description="详细结果")


class TaskStatsResponse(BaseModel):
    """任务统计响应模型"""
    total_tasks: int = Field(description="总任务数")
    status_distribution: Dict[str, int] = Field(description="状态分布")
    type_distribution: Dict[str, int] = Field(description="类型分布")
    celery_workers: int = Field(description="工作进程数")
    active_tasks: int = Field(description="活跃任务数")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(description="服务状态")
    timestamp: datetime = Field(description="检查时间")
    celery_status: str = Field(description="Celery状态")
    redis_status: Optional[str] = Field(None, description="Redis状态")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(description="错误信息")
    detail: Optional[str] = Field(None, description="详细错误")
    timestamp: datetime = Field(description="错误时间")
