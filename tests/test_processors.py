"""
处理器测试
"""
import pytest
from app.core.processor import ProcessorContext, ProcessorPipeline
from app.processors import (
    SubtitleDetectProcessor,
    SubtitleTranslateProcessor,
    AudioGenerateProcessor,
    AudioUploadProcessor
)


def test_processor_context():
    """测试处理器上下文"""
    context = ProcessorContext(
        video_id=123,
        platform="bilibili",
        data={"test": "data"}
    )
    
    assert context.video_id == 123
    assert context.platform == "bilibili"
    assert context.get("test") == "data"
    
    context.set("new_key", "new_value")
    assert context.get("new_key") == "new_value"
    
    context.add_metadata("meta_key", "meta_value")
    assert context.get_metadata("meta_key") == "meta_value"


def test_subtitle_detect_processor():
    """测试字幕检测处理器"""
    context = ProcessorContext(
        video_id=123,
        data={"subtitles": [{"text": "Hello world", "start_time": 0, "end_time": 5}]}
    )
    
    processor = SubtitleDetectProcessor()
    result = processor.execute(context)
    
    assert result["status"] == "success"
    assert "detected_language" in result["data"]


def test_subtitle_translate_processor():
    """测试字幕翻译处理器"""
    context = ProcessorContext(
        video_id=123,
        data={
            "subtitles": [{"text": "Hello world", "start_time": 0, "end_time": 5}],
            "detected_language": "en"
        }
    )
    
    processor = SubtitleTranslateProcessor()
    result = processor.execute(context)
    
    assert result["status"] == "success"
    assert "translated_subtitles" in result["data"]


def test_processor_pipeline():
    """测试处理器管道"""
    context = ProcessorContext(
        video_id=123,
        data={"subtitles": [{"text": "测试字幕", "start_time": 0, "end_time": 5}]}
    )
    
    pipeline = ProcessorPipeline([
        SubtitleDetectProcessor(),
        SubtitleTranslateProcessor()
    ])
    
    result = pipeline.execute(context)
    
    assert result["status"] in ["success", "partial_success"]
    assert result["total_steps"] == 2
    assert len(result["results"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
