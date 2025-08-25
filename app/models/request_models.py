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
