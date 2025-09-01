# 处理器架构说明

## 📁 处理器文件结构

现在每个处理器都独立在自己的文件中，便于维护和扩展：

```
app/processors/
├── __init__.py                      # 统一导出入口
├── language_detect_processor.py     # 语言检测处理器
├── translate_processor.py           # 翻译处理器
├── audio_generate_processor.py      # 音频生成处理器
└── upload_processor.py              # 上传处理器
```

## 🔧 处理器详解

### 1. LanguageDetectProcessor (语言检测)
**文件**: `language_detect_processor.py`

**功能**：
- 分析字幕文本内容
- 基于字符特征识别语言类型
- 支持中文、日语、英语识别

**输入**：
```json
{
  "subtitles": [
    {"text": "Hello world", "start": 0.0, "end": 2.0},
    {"text": "这是一个测试", "start": 2.0, "end": 4.0}
  ]
}
```

**输出**：
```json
{
  "detected_language": "zh-CN",
  "confidence": 0.95
}
```

### 2. TranslateProcessor (翻译)
**文件**: `translate_processor.py`

**功能**：
- 将检测到的文本翻译成目标语言
- 保留原始文本和时间信息
- 智能选择目标语言

**输入**：
```json
{
  "subtitles": [...],
  "detected_language": "zh-CN"
}
```

**输出**：
```json
{
  "translated_subtitles": [
    {
      "original_text": "这是一个测试",
      "translated_text": "[en] This is a test",
      "source_language": "zh-CN",
      "target_language": "en",
      "start": 2.0,
      "end": 4.0
    }
  ],
  "target_language": "en"
}
```

### 3. AudioGenerateProcessor (音频生成)
**文件**: `audio_generate_processor.py`

**功能**：
- 将翻译后的文本转换为语音文件
- 生成音频文件元信息
- 计算音频时长

**输入**：
```json
{
  "translated_subtitles": [...]
}
```

**输出**：
```json
{
  "audio_files": [
    {
      "index": 0,
      "filename": "audio_12345_0.mp3",
      "text": "[en] Hello world",
      "duration": 2.0,
      "language": "en"
    }
  ],
  "audio_count": 1
}
```

### 4. UploadProcessor (文件上传)
**文件**: `upload_processor.py`

**功能**：
- 将生成的音频文件上传到云存储
- 生成访问URL
- 记录上传状态

**输入**：
```json
{
  "audio_files": [...]
}
```

**输出**：
```json
{
  "uploaded_files": [
    {
      "filename": "audio_12345_0.mp3",
      "upload_url": "https://cdn.example.com/audio/audio_12345_0.mp3",
      "upload_time": 1672531200.0,
      "status": "uploaded"
    }
  ]
}
```

## 🚀 如何添加新处理器

### 1. 创建新处理器文件

例如创建 `subtitle_format_processor.py`：

```python
"""
字幕格式处理器 - 转换字幕格式
"""
from app.core.processor import BaseProcessor, ProcessorContext

class SubtitleFormatProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("字幕格式转换")
    
    def process(self, context: ProcessorContext) -> ProcessorContext:
        # 实现你的处理逻辑
        subtitles = context.get("translated_subtitles", [])
        
        # 转换为SRT格式
        srt_content = self._convert_to_srt(subtitles)
        
        context.set("srt_content", srt_content)
        return context
    
    def _convert_to_srt(self, subtitles):
        # SRT格式转换逻辑
        pass
```

### 2. 更新 `__init__.py`

```python
from .subtitle_format_processor import SubtitleFormatProcessor

__all__ = [
    "LanguageDetectProcessor",
    "TranslateProcessor",
    "AudioGenerateProcessor",
    "UploadProcessor",
    "SubtitleFormatProcessor"  # 新增
]
```

### 3. 在任务中使用

```python
pipeline = ProcessorPipeline([
    LanguageDetectProcessor(),
    TranslateProcessor(),
    SubtitleFormatProcessor(),  # 新增的处理器
    AudioGenerateProcessor(),
    UploadProcessor()
])
```

## 🎯 设计优势

### 1. 单一职责
- 每个处理器只负责一个特定功能
- 代码更清晰，更容易理解

### 2. 独立性
- 每个处理器可以独立开发和测试
- 减少相互依赖，降低耦合度

### 3. 可复用性
- 处理器可以在不同的任务链中复用
- 支持灵活的组合方式

### 4. 可维护性
- 修改一个处理器不会影响其他处理器
- 便于代码审查和版本控制

### 5. 可扩展性
- 添加新处理器非常简单
- 支持插件化的架构模式

## 🧪 测试建议

为每个处理器创建独立的测试文件：

```
tests/
├── test_language_detect_processor.py
├── test_translate_processor.py
├── test_audio_generate_processor.py
└── test_upload_processor.py
```

测试示例：
```python
def test_language_detect_processor():
    processor = LanguageDetectProcessor()
    context = ProcessorContext(
        video_id=123,
        data={"subtitles": [{"text": "Hello world"}]}
    )
    
    result_context = processor.process(context)
    assert result_context.get("detected_language") == "en"
```

这种架构模式是现代软件开发的最佳实践，特别适合学习和理解微服务架构的设计思想。
