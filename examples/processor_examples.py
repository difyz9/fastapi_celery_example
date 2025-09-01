#!/usr/bin/env python3
"""
处理器独立使用示例
展示如何单独使用每个处理器进行测试和开发
"""

from app.core.processor import ProcessorContext, ProcessorPipeline
from app.processors import (
    LanguageDetectProcessor,
    TranslateProcessor,
    AudioGenerateProcessor,
    UploadProcessor
)


def test_single_processor():
    """测试单个处理器"""
    print("🔍 测试单个处理器")
    
    # 创建测试数据
    context = ProcessorContext(
        video_id=12345,
        data={
            "subtitles": [
                {"text": "Hello world", "start": 0.0, "end": 2.0},
                {"text": "这是一个测试", "start": 2.0, "end": 4.0}
            ]
        }
    )
    
    # 测试语言检测处理器
    print("\n  📋 语言检测处理器：")
    detector = LanguageDetectProcessor()
    context = detector.process(context)
    print(f"    检测语言: {context.get('detected_language')}")
    print(f"    置信度: {context.get('confidence')}")


def test_partial_pipeline():
    """测试部分处理器组合"""
    print("\n🔗 测试部分处理器管道")
    
    context = ProcessorContext(
        video_id=12345,
        data={
            "subtitles": [
                {"text": "Hello world", "start": 0.0, "end": 2.0},
                {"text": "这是一个测试", "start": 2.0, "end": 4.0}
            ]
        }
    )
    
    # 只执行检测和翻译
    pipeline = ProcessorPipeline([
        LanguageDetectProcessor(),
        TranslateProcessor()
    ])
    
    result = pipeline.execute(context)
    print(f"  状态: {result['status']}")
    print(f"  执行的处理器: {result.get('processors_executed', [])}")
    
    if 'data' in result:
        translated = result['data'].get('translated_subtitles', [])
        if translated:
            print(f"  翻译示例: {translated[0].get('translated_text', 'N/A')}")


def test_full_pipeline():
    """测试完整处理器管道"""
    print("\n🚀 测试完整处理器管道")
    
    context = ProcessorContext(
        video_id=12345,
        data={
            "subtitles": [
                {"text": "Hello world", "start": 0.0, "end": 2.0},
                {"text": "这是一个测试", "start": 2.0, "end": 4.0}
            ]
        }
    )
    
    # 完整的处理链
    pipeline = ProcessorPipeline([
        LanguageDetectProcessor(),
        TranslateProcessor(),
        AudioGenerateProcessor(),
        UploadProcessor()
    ])
    
    result = pipeline.execute(context)
    print(f"  状态: {result['status']}")
    print(f"  执行时间: {result.get('total_execution_time', 0):.2f}秒")
    print(f"  处理器数量: {len(result.get('processors_executed', []))}")
    
    if 'data' in result:
        uploaded_files = result['data'].get('uploaded_files', [])
        print(f"  上传文件数: {len(uploaded_files)}")


def test_custom_combination():
    """测试自定义处理器组合"""
    print("\n🎯 测试自定义处理器组合")
    
    # 场景1：只做翻译，不生成音频
    print("  场景1: 只翻译不生成音频")
    context1 = ProcessorContext(
        video_id=11111,
        data={"subtitles": [{"text": "测试文本", "start": 0.0, "end": 1.0}]}
    )
    
    translate_only_pipeline = ProcessorPipeline([
        LanguageDetectProcessor(),
        TranslateProcessor()
    ])
    
    result1 = translate_only_pipeline.execute(context1)
    print(f"    结果: {result1['status']}")
    
    # 场景2：跳过翻译，直接音频处理（假设已有翻译数据）
    print("  场景2: 直接音频处理")
    context2 = ProcessorContext(
        video_id=22222,
        data={
            "translated_subtitles": [
                {
                    "translated_text": "Hello world",
                    "start_time": 0.0,
                    "end_time": 2.0,
                    "target_language": "en"
                }
            ]
        }
    )
    
    audio_only_pipeline = ProcessorPipeline([
        AudioGenerateProcessor(),
        UploadProcessor()
    ])
    
    result2 = audio_only_pipeline.execute(context2)
    print(f"    结果: {result2['status']}")


if __name__ == "__main__":
    print("🎪 处理器独立使用示例")
    print("=" * 50)
    
    try:
        test_single_processor()
        test_partial_pipeline()
        test_full_pipeline()
        test_custom_combination()
        
        print("\n✅ 所有测试完成!")
        print("📚 这展示了处理器独立文件架构的优势：")
        print("   - 每个处理器可以独立测试")
        print("   - 可以灵活组合不同的处理器")
        print("   - 易于调试和维护")
        print("   - 支持插件化扩展")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
