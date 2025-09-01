"""
处理器核心 - 展示任务链和解耦设计模式
这是学习案例的核心：如何设计可组合、可复用的处理单元
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass
from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessorContext:
    """
    处理器上下文 - 数据传递的载体
    
    设计要点：
    1. 统一的数据格式，便于处理器间传递
    2. 灵活的数据存储，支持任意类型数据
    3. 元数据支持，便于调试和监控
    """
    video_id: int
    data: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.metadata is None:
            self.metadata = {}
    
    def get(self, key: str, default=None):
        """获取数据"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置数据"""
        self.data[key] = value
    
    def add_metadata(self, key: str, value: Any):
        """添加元数据 - 用于调试和监控"""
        self.metadata[key] = value


class BaseProcessor(ABC):
    """
    基础处理器 - 所有处理器的基类
    
    设计模式：模板方法模式
    - execute() 定义执行框架（日志、异常处理）
    - process() 由子类实现具体逻辑
    """
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def process(self, context: ProcessorContext) -> ProcessorContext:
        """
        核心处理方法 - 子类必须实现
        
        设计原则：
        1. 输入输出都是 ProcessorContext
        2. 只关注自己的处理逻辑
        3. 不依赖其他处理器
        """
        pass
    
    def execute(self, context: ProcessorContext) -> Dict[str, Any]:
        """
        执行框架 - 统一的执行流程
        包含日志、异常处理、结果标准化
        """
        try:
            logger.info(f"🔄 执行处理器: {self.name}")
            
            # 调用具体处理逻辑
            updated_context = self.process(context)
            
            # 标准化返回结果
            result = {
                "status": "success",
                "processor": self.name,
                "video_id": updated_context.video_id,
                "data": updated_context.data,
                "metadata": updated_context.metadata,
                "message": f"{self.name} 处理完成"
            }
            
            logger.info(f"✅ 处理器 {self.name} 执行成功")
            return result
            
        except Exception as e:
            logger.error(f"❌ 处理器 {self.name} 执行失败: {e}")
            return {
                "status": "failed",
                "processor": self.name,
                "video_id": context.video_id,
                "error": str(e),
                "message": f"{self.name} 处理失败"
            }


class ProcessorPipeline:
    """
    处理器管道 - 任务链的核心实现
    
    设计模式：责任链模式
    将多个处理器连接成链，数据依次流过每个处理器
    """
    
    def __init__(self, processors: List[BaseProcessor]):
        self.processors = processors
    
    def execute(self, context: ProcessorContext) -> Dict[str, Any]:
        """
        执行处理器链
        
        核心逻辑：
        1. 按顺序执行每个处理器
        2. 前一个处理器的输出作为后一个的输入
        3. 任何环节失败都会停止整个链
        """
        results = []
        current_context = context
        
        try:
            logger.info(f"🚀 开始执行处理器管道，共 {len(self.processors)} 个步骤")
            
            for i, processor in enumerate(self.processors, 1):
                logger.info(f"📍 步骤 {i}/{len(self.processors)}: {processor.name}")
                
                # 执行单个处理器
                result = processor.execute(current_context)
                results.append(result)
                
                # 检查是否失败
                if result["status"] != "success":
                    logger.error(f"💥 管道在步骤 {i} 失败: {processor.name}")
                    break
                
                # 更新上下文，传递给下一个处理器
                current_context.data.update(result["data"])
                current_context.metadata.update(result["metadata"])
            
            # 构建管道结果
            success_count = sum(1 for r in results if r["status"] == "success")
            
            return {
                "status": "success" if success_count == len(self.processors) else "partial_success",
                "video_id": context.video_id,
                "total_steps": len(self.processors),
                "completed_steps": success_count,
                "results": results,
                "final_context": {
                    "data": current_context.data,
                    "metadata": current_context.metadata
                },
                "message": f"管道执行完成: {success_count}/{len(self.processors)} 成功"
            }
            
        except Exception as e:
            logger.error(f"❌ 处理器管道执行异常: {e}")
            return {
                "status": "failed",
                "video_id": context.video_id,
                "error": str(e),
                "results": results,
                "message": "管道执行异常"
            }
