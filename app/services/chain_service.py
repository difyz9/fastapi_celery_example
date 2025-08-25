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
                celery_app.signature('math.add', args=[a, b]),      # a + b
                celery_app.signature('math.multiply', args=[2]),    # 结果 * 2
                celery_app.signature('math.divide', args=[3])       # 结果 / 3
            )
        },
        "power_sqrt": {
            "description": "幂运算 -> 开方",
            "chain": lambda a, b: chain(
                celery_app.signature('math.power', args=[a, b]),    # a ^ b
                celery_app.signature('math.sqrt')                   # √结果
            )
        },
        "complex_math": {
            "description": "复杂数学运算链",
            "chain": lambda a, b: chain(
                celery_app.signature('math.add', args=[a, b]),          # a + b
                celery_app.signature('math.multiply', args=[a]),        # 结果 * a
                celery_app.signature('math.subtract', args=[b]),        # 结果 - b
                celery_app.signature('math.divide', args=[2])           # 结果 / 2
            )
        }
    }
    
    # Bilibili视频处理任务链
    BILIBILI_CHAINS = {
        "video_processing_chain": {
            "description": "Bilibili视频处理链: 字幕下载 -> 内容检查 -> 翻译 -> 语音合成 -> 上传COS",
            "chain": lambda video_data: chain(
                celery_app.signature('bilibili.download_subtitle', args=[video_data]),
                celery_app.signature('bilibili.check_subtitle_content'),
                celery_app.signature('bilibili.translate_subtitle'),
                celery_app.signature('bilibili.generate_speech'),
                celery_app.signature('bilibili.upload_to_cos')
            )
        },
        "subtitle_only_chain": {
            "description": "字幕处理链: 下载 -> 检查 -> 翻译",
            "chain": lambda video_data: chain(
                celery_app.signature('bilibili.download_subtitle', args=[video_data]),
                celery_app.signature('bilibili.check_subtitle_content'),
                celery_app.signature('bilibili.translate_subtitle')
            )
        },
        "speech_generation_chain": {
            "description": "语音生成链: 翻译 -> 语音合成 -> 上传",
            "chain": lambda translated_data: chain(
                celery_app.signature('bilibili.generate_speech', args=[translated_data]),
                celery_app.signature('bilibili.upload_to_cos')
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
