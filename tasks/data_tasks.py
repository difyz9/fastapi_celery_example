# tasks/data_tasks.py - 标准化的数据处理任务模块
from celery_app import app
from typing import List, Any, Dict
import time
import random

@app.task(name='data.fetch_data')
def fetch_data(source: str) -> List[int]:
    """
    获取数据任务
    
    Args:
        source: 数据源标识
        
    Returns:
        数据列表
    """
    print(f"📡 获取数据，来源: {source}")
    
    # 模拟从不同数据源获取数据
    if source == "test":
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    elif source == "random":
        data = [random.randint(1, 100) for _ in range(10)]
    else:
        data = [1, 2, 3]  # 默认数据
    
    # 模拟网络延迟
    time.sleep(0.5)
    
    print(f"✅ 数据获取完成: {data}")
    return data

@app.task(name='data.filter_data')
def filter_data(data: List[int], threshold: int) -> List[int]:
    """
    过滤数据任务
    
    Args:
        data: 输入数据列表
        threshold: 过滤阈值
        
    Returns:
        过滤后的数据列表
    """
    print(f"🔍 过滤数据，阈值: {threshold}")
    print(f"   输入数据: {data}")
    
    filtered = [x for x in data if x > threshold]
    
    print(f"✅ 过滤完成: {filtered}")
    return filtered

@app.task(name='data.sort_data')
def sort_data(data: List[int], reverse: bool = False) -> List[int]:
    """
    排序数据任务
    
    Args:
        data: 输入数据列表
        reverse: 是否降序排列
        
    Returns:
        排序后的数据列表
    """
    print(f"📊 排序数据，降序: {reverse}")
    print(f"   输入数据: {data}")
    
    sorted_data = sorted(data, reverse=reverse)
    
    print(f"✅ 排序完成: {sorted_data}")
    return sorted_data

@app.task(name='data.aggregate_results')
def aggregate_results(data: List[int]) -> Dict[str, Any]:
    """
    聚合结果任务
    
    Args:
        data: 输入数据列表
        
    Returns:
        聚合结果字典
    """
    print(f"📈 聚合数据: {data}")
    
    if not data:
        result = {"count": 0, "sum": 0, "avg": 0, "min": None, "max": None}
    else:
        result = {
            "count": len(data),
            "sum": sum(data),
            "avg": sum(data) / len(data),
            "min": min(data),
            "max": max(data)
        }
    
    print(f"✅ 聚合完成: {result}")
    return result

@app.task(name='data.calculate_statistics')
def calculate_statistics(data: List[int]) -> Dict[str, float]:
    """
    计算统计信息任务
    
    Args:
        data: 输入数据列表
        
    Returns:
        统计信息字典
    """
    print(f"📊 计算统计信息: {data}")
    
    if not data:
        return {"mean": 0, "variance": 0, "std_dev": 0}
    
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std_dev = variance ** 0.5
    
    result = {
        "mean": round(mean, 2),
        "variance": round(variance, 2),
        "std_dev": round(std_dev, 2)
    }
    
    print(f"✅ 统计完成: {result}")
    return result

@app.task(name='data.process_item')
def process_item(item: Any, operation: str = "double") -> Any:
    """
    处理单个数据项任务
    
    Args:
        item: 数据项
        operation: 操作类型 (double, square, negate)
        
    Returns:
        处理后的数据项
    """
    print(f"⚙️ 处理数据项: {item}, 操作: {operation}")
    
    if operation == "double":
        result = item * 2
    elif operation == "square":
        result = item ** 2
    elif operation == "negate":
        result = -item
    else:
        result = item  # 无操作
    
    print(f"✅ 处理完成: {result}")
    return result