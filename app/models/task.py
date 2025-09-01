"""
任务相关的数据模型 - 学习 Pydantic 数据验证
展示如何定义API的请求和响应模型
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    """
    任务提交请求模型
    
    学习要点：数据验证和类型约束
    """
    video_id: int = Field(..., description="视频ID", example=12345)
    subtitles: List[Dict[str, Any]] = Field(
        ..., 
        description="字幕数据列表",
        example=[
            {"text": "Hello world", "start": 0.0, "end": 2.0},
            {"text": "这是一个测试", "start": 2.0, "end": 4.0}
        ]
    )
    
    class Config:
        schema_extra = {
            "example": {
                "video_id": 12345,
                "subtitles": [
                    {"text": "Hello world", "start": 0.0, "end": 2.0},
                    {"text": "这是一个测试", "start": 2.0, "end": 4.0}
                ]
            }
        }


class TaskResponse(BaseModel):
    """
    任务提交响应模型
    
    学习要点：API响应的标准化格式
    """
    task_id: str = Field(..., description="任务ID")
    video_id: int = Field(..., description="视频ID")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="响应消息")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "abc123-def456-ghi789",
                "video_id": 12345,
                "status": "pending",
                "message": "任务已提交，正在处理中..."
            }
        }


class TaskStatus(BaseModel):
    """
    任务状态查询模型
    
    学习要点：任务生命周期状态管理
    """
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态：pending, running, completed, failed")
    message: str = Field(..., description="状态描述")
    progress: Optional[int] = Field(None, description="进度百分比(0-100)")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    error: Optional[str] = Field(None, description="错误信息")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "abc123-def456-ghi789",
                "status": "completed",
                "message": "任务执行成功",
                "progress": 100,
                "result": {
                    "detected_language": "chinese",
                    "translated_subtitles": [
                        {"text": "Hello world", "start": 0.0, "end": 2.0},
                        {"text": "This is a test", "start": 2.0, "end": 4.0}
                    ]
                }
            }
        }


# 处理器相关的模型
class ProcessorResult(BaseModel):
    """
    处理器执行结果模型
    
    学习要点：处理器输出的标准化
    """
    processor_name: str = Field(..., description="处理器名称")
    status: str = Field(..., description="执行状态")
    data: Dict[str, Any] = Field(..., description="处理结果数据")
    execution_time: float = Field(..., description="执行时间(秒)")
    message: str = Field(..., description="执行消息")
    
    class Config:
        schema_extra = {
            "example": {
                "processor_name": "LanguageDetectProcessor",
                "status": "success",
                "data": {
                    "detected_language": "chinese",
                    "confidence": 0.95
                },
                "execution_time": 0.25,
                "message": "语言检测完成"
            }
        }


class PipelineResult(BaseModel):
    """
    处理器管道执行结果模型
    
    学习要点：任务链执行结果的聚合
    """
    video_id: int = Field(..., description="视频ID")
    status: str = Field(..., description="管道执行状态")
    processors_executed: List[str] = Field(..., description="已执行的处理器列表")
    final_data: Dict[str, Any] = Field(..., description="最终结果数据")
    total_execution_time: float = Field(..., description="总执行时间(秒)")
    message: str = Field(..., description="执行消息")
    
    class Config:
        schema_extra = {
            "example": {
                "video_id": 12345,
                "status": "success",
                "processors_executed": [
                    "LanguageDetectProcessor",
                    "TranslateProcessor",
                    "AudioGenerateProcessor",
                    "UploadProcessor"
                ],
                "final_data": {
                    "detected_language": "chinese",
                    "translated_subtitles": [...],
                    "audio_files": [...],
                    "upload_urls": [...]
                },
                "total_execution_time": 15.5,
                "message": "视频字幕处理完成"
            }
        }
