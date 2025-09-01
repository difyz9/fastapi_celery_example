"""
上传处理器 - 将生成的文件上传到存储服务
学习要点：文件上传和云存储管理
"""
import time
from app.core.processor import BaseProcessor, ProcessorContext


class UploadProcessor(BaseProcessor):
    """
    上传处理器
    
    功能：将生成的文件上传到存储服务
    输入：音频文件信息
    输出：上传后的URL
    """
    
    def __init__(self):
        super().__init__("文件上传")
    
    def process(self, context: ProcessorContext) -> ProcessorContext:
        audio_files = context.get("audio_files", [])
        
        if not audio_files:
            raise ValueError("没有音频文件")
        
        # 模拟上传过程
        time.sleep(1.0)
        
        # 生成上传结果
        uploaded_files = []
        for audio_file in audio_files:
            uploaded_file = {
                **audio_file,
                "upload_url": f"https://cdn.example.com/audio/{audio_file['filename']}",
                "upload_time": time.time(),
                "status": "uploaded"
            }
            uploaded_files.append(uploaded_file)
        
        # 设置上传结果
        context.set("uploaded_files", uploaded_files)
        context.add_metadata("upload_count", len(uploaded_files))
        
        return context
