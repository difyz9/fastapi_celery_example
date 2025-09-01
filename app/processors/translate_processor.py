"""
翻译处理器 - 将字幕翻译成目标语言
学习要点：文本翻译和多语言处理
"""
import time
from app.core.processor import BaseProcessor, ProcessorContext


class TranslateProcessor(BaseProcessor):
    """
    翻译处理器
    
    功能：将字幕翻译成目标语言
    输入：原始字幕 + 检测到的语言
    输出：翻译后的字幕
    """
    
    def __init__(self):
        super().__init__("字幕翻译")
    
    def process(self, context: ProcessorContext) -> ProcessorContext:
        subtitles = context.get("subtitles", [])
        source_lang = context.get("detected_language", "unknown")
        
        if not subtitles:
            raise ValueError("没有字幕数据")
        
        # 模拟翻译过程
        time.sleep(1.0)
        
        # 确定目标语言
        target_lang = "en" if source_lang != "en" else "zh-CN"
        
        # 模拟翻译结果
        translated_subtitles = []
        for sub in subtitles:
            translated_sub = {
                **sub,
                "original_text": sub.get("text", ""),
                "translated_text": f"[{target_lang}] {sub.get('text', '')}",
                "source_language": source_lang,
                "target_language": target_lang
            }
            translated_subtitles.append(translated_sub)
        
        # 设置翻译结果
        context.set("translated_subtitles", translated_subtitles)
        context.set("target_language", target_lang)
        context.add_metadata("translation_count", len(translated_subtitles))
        
        return context
