# app/services/bilibili_chain_service.py - Bilibili视频处理任务链服务
from celery import chain
from celery_app import app as celery_app
from typing import Dict, Any

class BilibiliChainService:
    """Bilibili视频处理任务链服务"""
    
    # Bilibili视频处理任务链 - 使用Celery Chain确保任务顺序执行
    BILIBILI_CHAINS = {
        "video_processing_chain": {
            "description": "Bilibili视频处理链: 字幕下载 -> 内容检查 -> 翻译 -> 语音合成 -> 上传COS",
            "tasks": [
                "bilibili.download_subtitle",
                "bilibili.check_subtitle_content", 
                "bilibili.translate_subtitle",
                "bilibili.generate_speech",
                "bilibili.upload_to_cos"
            ],
            "chain": lambda video_data: chain(
                # 第一步：下载字幕（传入完整video_data）
                celery_app.signature('bilibili.download_subtitle', args=[video_data]),
                # 第二步：检查字幕内容（接收第一步的结果）
                celery_app.signature('bilibili.check_subtitle_content'),
                # 第三步：翻译字幕（接收第二步的结果）
                celery_app.signature('bilibili.translate_subtitle'),
                # 第四步：生成语音（接收第三步的结果）
                celery_app.signature('bilibili.generate_speech'),
                # 第五步：上传到COS（接收第四步的结果）
                celery_app.signature('bilibili.upload_to_cos')
            )
        },
        "subtitle_only_chain": {
            "description": "字幕处理链: 下载 -> 检查 -> 翻译",
            "tasks": [
                "bilibili.download_subtitle",
                "bilibili.check_subtitle_content",
                "bilibili.translate_subtitle"
            ],
            "chain": lambda video_data: chain(
                celery_app.signature('bilibili.download_subtitle', args=[video_data]),
                celery_app.signature('bilibili.check_subtitle_content'),
                celery_app.signature('bilibili.translate_subtitle')
            )
        },
        "speech_generation_chain": {
            "description": "语音生成链: 翻译 -> 语音合成 -> 上传",
            "tasks": [
                "bilibili.translate_subtitle",
                "bilibili.generate_speech",
                "bilibili.upload_to_cos"
            ],
            "chain": lambda subtitle_data: chain(
                celery_app.signature('bilibili.translate_subtitle', args=[subtitle_data]),
                celery_app.signature('bilibili.generate_speech'),
                celery_app.signature('bilibili.upload_to_cos')
            )
        },
        "content_analysis_chain": {
            "description": "内容分析链: 下载字幕 -> 内容检查",
            "tasks": [
                "bilibili.download_subtitle",
                "bilibili.check_subtitle_content"
            ],
            "chain": lambda video_data: chain(
                celery_app.signature('bilibili.download_subtitle', args=[video_data]),
                celery_app.signature('bilibili.check_subtitle_content')
            )
        },
        "translation_chain": {
            "description": "翻译处理链: 内容检查 -> 翻译 -> 语音合成",
            "tasks": [
                "bilibili.check_subtitle_content",
                "bilibili.translate_subtitle",
                "bilibili.generate_speech"
            ],
            "chain": lambda subtitle_data: chain(
                celery_app.signature('bilibili.check_subtitle_content', args=[subtitle_data]),
                celery_app.signature('bilibili.translate_subtitle'),
                celery_app.signature('bilibili.generate_speech')
            )
        }
    }
    
    @classmethod
    def get_available_chains(cls) -> Dict[str, Dict]:
        """获取可用的Bilibili任务链"""
        return {
            name: {
                "description": chain_info["description"],
                "tasks": chain_info["tasks"]
            }
            for name, chain_info in cls.BILIBILI_CHAINS.items()
        }
    
    @classmethod
    def is_valid_chain(cls, chain_name: str) -> bool:
        """验证任务链是否有效"""
        return chain_name in cls.BILIBILI_CHAINS
    
    @classmethod
    def create_chain(cls, chain_name: str, video_data: Dict[str, Any]):
        """创建Bilibili视频处理任务链"""
        if chain_name not in cls.BILIBILI_CHAINS:
            raise ValueError(f"不支持的Bilibili任务链: {chain_name}")
        
        chain_info = cls.BILIBILI_CHAINS[chain_name]
        return chain_info["chain"](video_data)
    
    @classmethod
    def get_chain_description(cls, chain_name: str) -> str:
        """获取任务链描述"""
        if chain_name in cls.BILIBILI_CHAINS:
            return cls.BILIBILI_CHAINS[chain_name]["description"]
        else:
            return "未知Bilibili任务链"
    
    @classmethod
    def get_chain_tasks(cls, chain_name: str) -> list:
        """获取任务链包含的任务列表"""
        if chain_name in cls.BILIBILI_CHAINS:
            return cls.BILIBILI_CHAINS[chain_name]["tasks"]
        else:
            return []
    
    @classmethod
    def execute_chain(cls, chain_name: str, video_data: Dict[str, Any]):
        """执行Bilibili视频处理任务链"""
        try:
            task_chain = cls.create_chain(chain_name, video_data)
            result = task_chain.apply_async()
            return {
                "chain_id": result.id,
                "chain_name": chain_name,
                "status": "submitted",
                "description": cls.get_chain_description(chain_name),
                "tasks": cls.get_chain_tasks(chain_name),
                "video_info": {
                    "bvid": video_data.get("bvid"),
                    "title": video_data.get("title"),
                    "author": video_data.get("author")
                }
            }
        except Exception as e:
            raise Exception(f"执行Bilibili任务链失败: {str(e)}")
    
    @classmethod
    def validate_video_data(cls, video_data: Dict[str, Any]) -> bool:
        """验证视频数据格式"""
        required_fields = ["bvid", "title", "author"]
        return all(field in video_data for field in required_fields)
    
    @classmethod
    def get_supported_formats(cls) -> Dict[str, Any]:
        """获取支持的视频格式和参数"""
        return {
            "video_formats": ["MP4", "AVI", "FLV"],
            "subtitle_formats": ["SRT", "ASS", "VTT"],
            "audio_formats": ["WAV", "MP3", "AAC"],
            "max_duration": 7200,  # 最大时长（秒）
            "max_file_size": "500MB"
        }
