# app/services/chain_service.py - 任务链服务
from celery import chain
from celery_app import app as celery_app
from typing import Dict, Any

class ChainService:
    """任务链服务"""
    
    # 数学任务链定义
    OPERATION_CHAINS = {
        "add_multiply_divide": {
            "description": "加法 -> 乘法 -> 除法",
            "chain": lambda a, b: chain(
                celery_app.tasks['math.add'].s(a, b),      # a + b
                celery_app.tasks['math.multiply'].s(2),    # 结果 * 2
                celery_app.tasks['math.divide'].s(3)       # 结果 / 3
            )
        },
        "power_sqrt": {
            "description": "幂运算 -> 开方",
            "chain": lambda a, b: chain(
                celery_app.tasks['math.power'].s(a, b),    # a ^ b
                celery_app.tasks['math.sqrt'].s()          # √结果
            )
        },
        "complex_math": {
            "description": "复杂数学运算链",
            "chain": lambda a, b: chain(
                celery_app.tasks['math.add'].s(a, b),          # a + b
                celery_app.tasks['math.multiply'].s(a),        # 结果 * a
                celery_app.tasks['math.subtract'].s(b),        # 结果 - b
                celery_app.tasks['math.divide'].s(2)           # 结果 / 2
            )
        }
    }
    
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
                celery_app.tasks['bilibili.download_subtitle'].s(video_data),
                # 第二步：检查字幕内容（接收第一步的结果）
                celery_app.tasks['bilibili.check_subtitle_content'].s(),
                # 第三步：翻译字幕（接收第二步的结果）
                celery_app.tasks['bilibili.translate_subtitle'].s(),
                # 第四步：生成语音（接收第三步的结果）
                celery_app.tasks['bilibili.generate_speech'].s(),
                # 第五步：上传到COS（接收第四步的结果）
                celery_app.tasks['bilibili.upload_to_cos'].s()
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
                celery_app.tasks['bilibili.download_subtitle'].s(video_data),
                celery_app.tasks['bilibili.check_subtitle_content'].s(),
                celery_app.tasks['bilibili.translate_subtitle'].s()
            )
        },
        "speech_generation_chain": {
            "description": "语音生成链: 语音合成 -> 上传",
            "tasks": [
                "bilibili.generate_speech",
                "bilibili.upload_to_cos"
            ],
            "chain": lambda translated_data: chain(
                celery_app.tasks['bilibili.generate_speech'].s(translated_data),
                celery_app.tasks['bilibili.upload_to_cos'].s()
            )
        }
    }
    
    @classmethod
    def get_available_chains(cls):
        """获取可用的任务链"""
        return {
            "math_chains": {
                name: {"description": chain_info["description"]}
                for name, chain_info in cls.OPERATION_CHAINS.items()
            },
            "bilibili_chains": {
                name: {"description": chain_info["description"]}
                for name, chain_info in cls.BILIBILI_CHAINS.items()
            }
        }
    
    @classmethod
    def is_valid_chain(cls, chain_name: str) -> bool:
        """验证任务链是否有效"""
        return (chain_name in cls.OPERATION_CHAINS or 
                chain_name in cls.BILIBILI_CHAINS)
    
    @classmethod
    def create_math_chain(cls, chain_name: str, a: int, b: int):
        """创建数学任务链"""
        if chain_name not in cls.OPERATION_CHAINS:
            raise ValueError(f"不支持的数学任务链: {chain_name}")
        
        chain_info = cls.OPERATION_CHAINS[chain_name]
        return chain_info["chain"](a, b)
    
    @classmethod
    def create_bilibili_chain(cls, chain_name: str, video_data: Dict[str, Any]):
        """创建Bilibili视频处理任务链"""
        if chain_name not in cls.BILIBILI_CHAINS:
            raise ValueError(f"不支持的Bilibili任务链: {chain_name}")
        
        chain_info = cls.BILIBILI_CHAINS[chain_name]
        return chain_info["chain"](video_data)
    
    @classmethod
    def get_chain_description(cls, chain_name: str) -> str:
        """获取任务链描述"""
        if chain_name in cls.OPERATION_CHAINS:
            return cls.OPERATION_CHAINS[chain_name]["description"]
        elif chain_name in cls.BILIBILI_CHAINS:
            return cls.BILIBILI_CHAINS[chain_name]["description"]
        else:
            return "未知任务链"
