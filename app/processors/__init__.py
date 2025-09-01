"""
处理器模块 - 统一导出所有处理器
每个处理器都在独立的文件中，便于维护和测试
"""
from .language_detect_processor import LanguageDetectProcessor
from .translate_processor import TranslateProcessor
from .audio_generate_processor import AudioGenerateProcessor
from .upload_processor import UploadProcessor

__all__ = [
    "LanguageDetectProcessor",
    "TranslateProcessor", 
    "AudioGenerateProcessor",
    "UploadProcessor"
]