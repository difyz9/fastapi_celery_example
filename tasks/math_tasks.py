# tasks/math_tasks.py - 标准化的数学任务模块
from celery_app import app
from typing import Union
import time

@app.task(name='math.add')
def add(x: Union[int, float], y: Union[int, float]) -> Union[int, float]:
    """
    加法任务
    
    Args:
        x: 第一个数
        y: 第二个数
        
    Returns:
        两数之和
    """
    print(f"🔢 执行加法: {x} + {y}")
    result = x + y
    print(f"✅ 加法结果: {result}")
    return result

@app.task(name='math.multiply')
def multiply(x: Union[int, float], y: Union[int, float]) -> Union[int, float]:
    """
    乘法任务
    
    Args:
        x: 被乘数
        y: 乘数
        
    Returns:
        两数之积
    """
    print(f"🔢 执行乘法: {x} * {y}")
    result = x * y
    print(f"✅ 乘法结果: {result}")
    return result

@app.task(name='math.subtract')
def subtract(x: Union[int, float], y: Union[int, float]) -> Union[int, float]:
    """
    减法任务
    
    Args:
        x: 被减数
        y: 减数
        
    Returns:
        两数之差
    """
    print(f"🔢 执行减法: {x} - {y}")
    result = x - y
    print(f"✅ 减法结果: {result}")
    return result

@app.task(name='math.divide')
def divide(x: Union[int, float], y: Union[int, float]) -> Union[int, float]:
    """
    除法任务
    
    Args:
        x: 被除数
        y: 除数
        
    Returns:
        两数之商
        
    Raises:
        ValueError: 当除数为零时
    """
    if y == 0:
        raise ValueError("除数不能为零")
    
    print(f"🔢 执行除法: {x} / {y}")
    result = x / y
    print(f"✅ 除法结果: {result}")
    return result

@app.task(name='math.power')
def power(base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
    """
    幂运算任务
    
    Args:
        base: 底数
        exponent: 指数
        
    Returns:
        幂运算结果
    """
    print(f"🔢 执行幂运算: {base} ** {exponent}")
    result = base ** exponent
    print(f"✅ 幂运算结果: {result}")
    return result

@app.task(name='math.sqrt')
def sqrt(x: Union[int, float]) -> float:
    """
    平方根任务
    
    Args:
        x: 被开方数
        
    Returns:
        平方根结果
        
    Raises:
        ValueError: 当输入为负数时
    """
    if x < 0:
        raise ValueError("不能对负数开平方根")
    
    import math
    print(f"🔢 执行开方: √{x}")
    result = math.sqrt(x)
    print(f"✅ 开方结果: {result}")
    return result