# workflows/data_workflow.py - 标准化的数据工作流
from celery import chain, group, chord
from tasks.math_tasks import add, multiply
from tasks.data_tasks import fetch_data, process_item, filter_data, aggregate_results
from tasks.io_tasks import save_to_database, generate_report
from .workflow_manager import workflow_manager

def create_math_workflow(x: float, y: float, z: float):
    """
    创建数学计算工作流: (x + y) * z
    
    Args:
        x: 第一个数
        y: 第二个数  
        z: 乘数
        
    Returns:
        工作流结果
    """
    workflow = chain(
        add.s(x, y),
        multiply.s(z)
    )
    
    result = workflow.apply_async()
    workflow_result = workflow_manager.register_workflow(
        "math_workflow",
        [result.id]
    )
    
    return result, workflow_result

def create_data_processing_workflow(source: str, threshold: float, multiplier: float):
    """
    创建数据处理工作流: 获取数据 -> 过滤 -> 并行处理 -> 聚合 -> 保存
    
    Args:
        source: 数据源
        threshold: 过滤阈值
        multiplier: 处理乘数
        
    Returns:
        工作流结果
    """
    # 数据获取和过滤
    data_prep = chain(
        fetch_data.s(source),
        filter_data.s(threshold)
    )
    
    # 并行处理和聚合
    def parallel_processing(data):
        if not data:
            return aggregate_results.s([])
        
        # 为每个数据项创建处理任务
        processing_tasks = [process_item.s(item, multiplier) for item in data]
        
        # 使用 chord 进行并行处理和聚合
        return chord(processing_tasks)(aggregate_results.s())
    
    # 保存结果
    def save_results(aggregated_result):
        return save_to_database.s(aggregated_result, "processed_data")
    
    # 组合完整工作流
    workflow = chain(
        data_prep,
        parallel_processing,
        save_results
    )
    
    result = workflow.apply_async()
    workflow_result = workflow_manager.register_workflow(
        "data_processing_workflow", 
        [result.id]
    )
    
    return result, workflow_result

def create_comprehensive_workflow(x: float, y: float, z: float, source: str):
    """
    创建综合工作流: 数学计算 + 数据处理 + 报告生成
    
    Args:
        x: 数学计算参数1
        y: 数学计算参数2
        z: 数学计算参数3
        source: 数据源
        
    Returns:
        工作流结果
    """
    # 数学计算分支
    math_branch = chain(
        add.s(x, y),
        multiply.s(z)
    )
    
    # 数据处理分支
    data_branch = chain(
        fetch_data.s(source),
        filter_data.s(2)  # 过滤大于2的数据
    )
    
    # 并行执行数学计算和数据处理
    parallel_phase = group(math_branch, data_branch)
    
    # 结果处理
    def process_results(results):
        math_result, data_result = results
        # 生成包含两种结果的报告
        return generate_report.s({
            "math_result": math_result,
            "data_result": data_result
        }, "comprehensive")
    
    # 完整工作流
    workflow = chain(
        parallel_phase,
        process_results
    )
    
    result = workflow.apply_async()
    workflow_result = workflow_manager.register_workflow(
        "comprehensive_workflow",
        [result.id]
    )
    
    return result, workflow_result