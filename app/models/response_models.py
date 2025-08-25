# app/models/response_models.py - 响应模型
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TaskResponse(BaseModel):
    """任务提交响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="响应消息")
    request_data: Dict[str, Any] = Field(..., description="请求数据")

class TaskStatusResponse(BaseModel):
    """任务状态查询响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    result: Optional[Any] = Field(None, description="任务结果")
    error: Optional[str] = Field(None, description="错误信息")
    created_at: str = Field(..., description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")

class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    total: int = Field(..., description="总任务数")
    limit: int = Field(..., description="每页限制")
    offset: int = Field(..., description="偏移量")
    tasks: list = Field(..., description="任务列表")
