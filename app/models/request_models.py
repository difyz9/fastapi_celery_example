# app/models/request_models.py - 请求模型
from pydantic import BaseModel, Field
from typing import Optional

class MathRequest(BaseModel):
    """数学运算请求模型"""
    a: int = Field(..., description="第一个操作数", example=10)
    b: int = Field(..., description="第二个操作数", example=5)
    operation_chain: Optional[str] = Field(
        default="add_multiply_divide", 
        description="运算链类型",
        example="add_multiply_divide"
    )

    class Config:
        schema_extra = {
            "example": {
                "a": 10,
                "b": 5,
                "operation_chain": "add_multiply_divide"
            }
        }

class BilibiliVideoCreate(BaseModel):
    """创建Bilibili视频请求模型 - 匹配前端真实数据结构"""
    title: str = Field(..., description="视频标题", max_length=500)
    aid: int = Field(..., description="视频AID")
    bvid: Optional[str] = Field(None, description="Bilibili视频ID", max_length=20)
    cid: int = Field(..., description="分集ID")
    author: str = Field(..., description="UP主名称", max_length=200)
    currentPart: int = Field(..., description="当前分集", ge=1)
    isCollection: bool = Field(..., description="是否为合集")
    totalParts: int = Field(..., description="总分集数", ge=1)
    url: str = Field(..., description="视频URL", max_length=500)
    duration: float = Field(..., description="视频时长(秒)", ge=0)
    submittedAt: str = Field(..., description="提交时间戳")
    source: str = Field(..., description="数据来源", max_length=100)
    currentPlayTime: float = Field(..., description="当前视频时间轴", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "油管Flutter 大师班 - FULL FLUTTER COURSES",
                "aid": 1254761143,
                "bvid": "BV1AJ4m1P7MY",
                "cid": 1557321576,
                "author": "精选海外教程postcode",
                "currentPart": 6,
                "isCollection": True,
                "totalParts": 16,
                "url": "https://www.bilibili.com/video/BV1AJ4m1P7MY?p=6",
                "duration": 2997,
                "submittedAt": "2025-08-19T16:59:58.783Z",
                "source": "chrome_extension",
                "currentPlayTime": 1200.5
            }
        }
