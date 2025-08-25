# app/services/chain_service.py - 任务链服务
from celery import chain
from celery_app import app as celery_app

class ChainService:
    """任务链服务"""
    
    # 任务链定义
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
    
    @classmethod
    def get_available_chains(cls):
        """获取可用的任务链"""
        return {
            name: {"description": chain_info["description"]}
            for name, chain_info in cls.OPERATION_CHAINS.items()
        }
    
    @classmethod
    def is_valid_chain(cls, chain_name: str) -> bool:
        """验证任务链是否有效"""
        return chain_name in cls.OPERATION_CHAINS
    
    @classmethod
    def create_chain(cls, chain_name: str, a: int, b: int):
        """创建任务链"""
        if not cls.is_valid_chain(chain_name):
            raise ValueError(f"不支持的任务链: {chain_name}")
        
        chain_info = cls.OPERATION_CHAINS[chain_name]
        return chain_info["chain"](a, b)
    
    @classmethod
    def get_chain_description(cls, chain_name: str) -> str:
        """获取任务链描述"""
        if not cls.is_valid_chain(chain_name):
            return "未知任务链"
        
        return cls.OPERATION_CHAINS[chain_name]["description"]
