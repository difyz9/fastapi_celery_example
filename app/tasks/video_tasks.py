"""
Celery 任务定义 - 异步任务队列的实现
展示如何将处理器管道与 Celery 结合
"""
from typing import Dict, Any
from app.core.celery_app import celery_app
from app.core.logger import get_logger
from app.core.processor import ProcessorContext, ProcessorPipeline
from app.processors import (
    LanguageDetectProcessor,
    TranslateProcessor,
    AudioGenerateProcessor,
    UploadProcessor
)

logger = get_logger(__name__)


@celery_app.task(bind=True, name="process_video_subtitles")
def process_video_subtitles(self, video_id: int, subtitles: list) -> Dict[str, Any]:
    """
    完整的视频字幕处理任务 - 展示完整的任务链
    
    任务链：语言检测 → 翻译 → 音频生成 → 上传
    """
    task_id = self.request.id
    logger.info(f"🎬 开始处理视频字幕 [任务ID: {task_id}]")
    
    try:
        # 创建处理上下文
        context = ProcessorContext(
            video_id=video_id,
            data={"subtitles": subtitles}
        )
        context.add_metadata("task_id", task_id)
        
        # 构建处理器管道 - 这是学习的重点
        pipeline = ProcessorPipeline([
            LanguageDetectProcessor(),   # 步骤1：检测语言
            TranslateProcessor(),        # 步骤2：翻译字幕 
            AudioGenerateProcessor(),    # 步骤3：生成音频
            UploadProcessor()            # 步骤4：上传文件
        ])
        
        # 执行管道
        result = pipeline.execute(context)
        result["task_id"] = task_id
        
        logger.info(f"✅ 视频字幕处理完成 [任务ID: {task_id}]")
        return result
        
    except Exception as e:
        logger.error(f"❌ 视频字幕处理失败 [任务ID: {task_id}]: {e}")
        return {
            "task_id": task_id,
            "video_id": video_id,
            "status": "failed",
            "error": str(e)
        }


@celery_app.task(bind=True, name="detect_language_only")
def detect_language_only(self, video_id: int, subtitles: list) -> Dict[str, Any]:
    """
    单步任务示例 - 只进行语言检测
    展示如何使用单个处理器
    """
    task_id = self.request.id
    logger.info(f"🔍 开始语言检测 [任务ID: {task_id}]")
    
    try:
        # 创建上下文
        context = ProcessorContext(
            video_id=video_id,
            data={"subtitles": subtitles}
        )
        
        # 执行单个处理器
        processor = LanguageDetectProcessor()
        result = processor.execute(context)
        result["task_id"] = task_id
        
        logger.info(f"✅ 语言检测完成 [任务ID: {task_id}]")
        return result
        
    except Exception as e:
        logger.error(f"❌ 语言检测失败 [任务ID: {task_id}]: {e}")
        return {
            "task_id": task_id,
            "video_id": video_id,
            "status": "failed",
            "error": str(e)
        }


# 任务构建器 - 演示如何组合不同的处理器
class TaskBuilder:
    """
    任务构建器 - 展示任务链的灵活组合
    这是解耦设计的体现：不同的业务需求可以组合不同的处理器
    """
    
    @staticmethod
    def create_pipeline(processors: list, video_id: int, data: dict) -> Dict[str, Any]:
        """创建自定义处理器管道"""
        context = ProcessorContext(video_id=video_id, data=data)
        pipeline = ProcessorPipeline(processors)
        return pipeline.execute(context)
    
    @staticmethod
    def detect_only(video_id: int, subtitles: list) -> Dict[str, Any]:
        """只检测语言"""
        return TaskBuilder.create_pipeline(
            [LanguageDetectProcessor()],
            video_id,
            {"subtitles": subtitles}
        )
    
    @staticmethod
    def detect_and_translate(video_id: int, subtitles: list) -> Dict[str, Any]:
        """检测 + 翻译"""
        return TaskBuilder.create_pipeline(
            [LanguageDetectProcessor(), TranslateProcessor()],
            video_id,
            {"subtitles": subtitles}
        )
    
    @staticmethod
    def full_pipeline(video_id: int, subtitles: list) -> Dict[str, Any]:
        """完整处理链"""
        return TaskBuilder.create_pipeline(
            [
                LanguageDetectProcessor(),
                TranslateProcessor(),
                AudioGenerateProcessor(),
                UploadProcessor()
            ],
            video_id,
            {"subtitles": subtitles}
        )
