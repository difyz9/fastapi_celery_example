"""
语言检测处理器 - 分析字幕文本，识别语言类型
学习要点：自然语言处理的基础应用
"""
import time
from app.core.processor import BaseProcessor, ProcessorContext


class LanguageDetectProcessor(BaseProcessor):
    """
    语言检测处理器
    
    功能：分析字幕文本，识别语言类型
    输入：字幕文本列表
    输出：检测到的语言和置信度
    """
    
    def __init__(self):
        super().__init__("语言检测")
    
    def process(self, context: ProcessorContext) -> ProcessorContext:
        subtitles = context.get("subtitles", [])
        
        if not subtitles:
            raise ValueError("没有字幕数据")
        
        # 模拟语言检测过程
        time.sleep(0.5)  # 模拟处理时间
        
        # 简单的语言检测逻辑（基于字符特征）
        sample_text = " ".join([sub.get("text", "") for sub in subtitles[:3]])
        
        # 基于字符判断语言
        if any('\u4e00' <= char <= '\u9fff' for char in sample_text):
            detected_language = "zh-CN"  # 中文
        elif any('\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' for char in sample_text):
            detected_language = "ja"      # 日语
        else:
            detected_language = "en"      # 英语
        
        # 设置检测结果
        context.set("detected_language", detected_language)
        context.set("confidence", 0.95)
        context.add_metadata("sample_text", sample_text[:50])
        
        return context
