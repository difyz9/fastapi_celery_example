# app/services/math_chain_service.py - 数学任务链服务
from celery import chain
from celery_app import app as celery_app
from typing import Dict, Any

class MathChainService:
    """数学任务链服务"""
    
    # 数学任务链定义
    OPERATION_CHAINS = {
        "add_multiply_divide": {
            "description": "加法 -> 乘法 -> 除法",
            "tasks": ["math.add", "math.multiply", "math.divide"],
            "chain": lambda a, b: chain(
                celery_app.signature('math.add', args=[a, b]),      # a + b
                celery_app.signature('math.multiply', args=[2]),    # 结果 * 2
                celery_app.signature('math.divide', args=[3])       # 结果 / 3
            )
        },
        "power_sqrt": {
            "description": "幂运算 -> 开方",
            "tasks": ["math.power", "math.sqrt"],
            "chain": lambda a, b: chain(
                celery_app.signature('math.power', args=[a, b]),    # a ^ b
                celery_app.signature('math.sqrt')                   # √结果
            )
        },
        "complex_math": {
            "description": "复杂数学运算链",
            "tasks": ["math.add", "math.multiply", "math.subtract", "math.divide"],
            "chain": lambda a, b: chain(
                celery_app.signature('math.add', args=[a, b]),          # a + b
                celery_app.signature('math.multiply', args=[a]),        # 结果 * a
                celery_app.signature('math.subtract', args=[b]),        # 结果 - b
                celery_app.signature('math.divide', args=[2])           # 结果 / 2
            )
        },
        "fibonacci_sequence": {
            "description": "斐波那契数列计算链",
            "tasks": ["math.add", "math.multiply"],
            "chain": lambda a, b: chain(
                celery_app.signature('math.add', args=[a, b]),          # a + b
                celery_app.signature('math.multiply', args=[a]),        # 结果 * a
                celery_app.signature('math.add', args=[b])              # 结果 + b
            )
        },
        "quadratic_formula": {
            "description": "二次方程求解链",
            "tasks": ["math.power", "math.multiply", "math.subtract", "math.sqrt"],
            "chain": lambda a, b: chain(
                celery_app.signature('math.power', args=[b, 2]),        # b²
                celery_app.signature('math.multiply', args=[4]),        # 4 * b²
                celery_app.signature('math.multiply', args=[a]),        # a * 4 * b²
                celery_app.signature('math.subtract', args=[0]),        # 0 - (a * 4 * b²)
                celery_app.signature('math.sqrt')                       # √结果
            )
        }
    }
    
    @classmethod
    def get_available_chains(cls) -> Dict[str, Dict]:
        """获取可用的数学任务链"""
        return {
            name: {
                "description": chain_info["description"],
                "tasks": chain_info["tasks"]
            }
            for name, chain_info in cls.OPERATION_CHAINS.items()
        }
    
    @classmethod
    def is_valid_chain(cls, chain_name: str) -> bool:
        """验证任务链是否有效"""
        return chain_name in cls.OPERATION_CHAINS
    
    @classmethod
    def create_chain(cls, chain_name: str, params: Dict[str, Any]):
        """创建数学任务链"""
        if chain_name not in cls.OPERATION_CHAINS:
            raise ValueError(f"不支持的数学任务链: {chain_name}")
        
        # 从参数字典中提取a和b
        a = params.get("a")
        b = params.get("b")
        
        if a is None or b is None:
            raise ValueError("数学任务链需要参数 a 和 b")
        
        chain_info = cls.OPERATION_CHAINS[chain_name]
        return chain_info["chain"](a, b)
    
    @classmethod
    def get_chain_description(cls, chain_name: str) -> str:
        """获取任务链描述"""
        if chain_name in cls.OPERATION_CHAINS:
            return cls.OPERATION_CHAINS[chain_name]["description"]
        else:
            return "未知数学任务链"
    
    @classmethod
    def get_chain_tasks(cls, chain_name: str) -> list:
        """获取任务链包含的任务列表"""
        if chain_name in cls.OPERATION_CHAINS:
            return cls.OPERATION_CHAINS[chain_name]["tasks"]
        else:
            return []
    
    @classmethod
    def execute_chain(cls, chain_name: str, params: Dict[str, Any]):
        """执行数学任务链"""
        try:
            task_chain = cls.create_chain(chain_name, params)
            result = task_chain.apply_async()
            return {
                "chain_id": result.id,
                "chain_name": chain_name,
                "status": "submitted",
                "description": cls.get_chain_description(chain_name),
                "tasks": cls.get_chain_tasks(chain_name),
                "input_params": {"a": params.get("a"), "b": params.get("b")}
            }
        except Exception as e:
            raise Exception(f"执行数学任务链失败: {str(e)}")
