# workflows/workflow_manager.py - 工作流管理器
from celery import chain, group, chord
from typing import List, Any, Dict, Optional
from dataclasses import dataclass
import uuid
from datetime import datetime

@dataclass
class WorkflowResult:
    """工作流执行结果"""
    workflow_id: str
    workflow_type: str
    task_ids: List[str]
    start_time: datetime
    status: str = "submitted"

class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowResult] = {}
    
    def create_workflow_id(self) -> str:
        """创建工作流ID"""
        return f"workflow_{uuid.uuid4().hex[:8]}"
    
    def register_workflow(self, workflow_type: str, task_ids: List[str]) -> WorkflowResult:
        """注册工作流"""
        workflow_id = self.create_workflow_id()
        result = WorkflowResult(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            task_ids=task_ids,
            start_time=datetime.now()
        )
        self.workflows[workflow_id] = result
        return result
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowResult]:
        """获取工作流状态"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[WorkflowResult]:
        """列出所有工作流"""
        return list(self.workflows.values())

# 全局工作流管理器实例
workflow_manager = WorkflowManager()

class StandardWorkflows:
    """标准工作流集合"""
    
    @staticmethod
    def math_calculation_chain(x: float, y: float, z: float):
        """数学计算链：(x + y) * z"""
        from tasks.math_tasks import add, multiply
        
        workflow = chain(
            add.s(x, y),
            multiply.s(z)
        )
        
        result = workflow.apply_async()
        workflow_result = workflow_manager.register_workflow(
            "math_calculation_chain",
            [result.id]
        )
        
        return result, workflow_result
    
    @staticmethod
    def data_processing_pipeline(source: str, threshold: float, multiplier: float):
        """数据处理管道：获取 -> 过滤 -> 处理 -> 聚合"""
        from tasks.data_tasks import fetch_data, filter_data, process_item, aggregate_results
        
        # 获取数据并过滤
        data_chain = chain(
            fetch_data.s(source),
            filter_data.s(threshold)
        )
        
        # 处理每个数据项（并行）
        def process_parallel(data):
            if not data:
                return aggregate_results.s([])
            
            processing_tasks = [process_item.s(item, multiplier) for item in data]
            return chord(processing_tasks)(aggregate_results.s())
        
        # 组合成完整工作流
        workflow = chain(
            data_chain,
            process_parallel
        )
        
        result = workflow.apply_async()
        workflow_result = workflow_manager.register_workflow(
            "data_processing_pipeline",
            [result.id]
        )
        
        return result, workflow_result
    
    @staticmethod
    def report_generation_workflow(data_source: str, report_type: str, recipients: List[str]):
        """报告生成工作流：数据获取 -> 统计分析 -> 生成报告 -> 发送通知"""
        from tasks.data_tasks import fetch_data, calculate_statistics
        from tasks.io_tasks import generate_report, send_email
        
        # 数据分析链
        analysis_chain = chain(
            fetch_data.s(data_source),
            calculate_statistics.s()
        )
        
        # 报告生成和发送（并行）
        def generate_and_send(stats_data):
            report_task = generate_report.s(stats_data, report_type)
            email_tasks = [
                send_email.s(recipient, f"{report_type}报告", "报告已生成完成")
                for recipient in recipients
            ]
            
            return group([report_task] + email_tasks)
        
        # 完整工作流
        workflow = chain(
            analysis_chain,
            generate_and_send
        )
        
        result = workflow.apply_async()
        workflow_result = workflow_manager.register_workflow(
            "report_generation_workflow",
            [result.id]
        )
        
        return result, workflow_result
    
    @staticmethod
    def comprehensive_etl_workflow(source: str, transformations: Dict[str, Any], output_config: Dict[str, Any]):
        """
        综合ETL工作流：提取 -> 转换 -> 加载
        
        Args:
            source: 数据源
            transformations: 转换配置
            output_config: 输出配置
        """
        from tasks.data_tasks import fetch_data, filter_data, sort_data, calculate_statistics
        from tasks.io_tasks import save_to_database, backup_data, send_notification
        
        # 提取阶段
        extract_task = fetch_data.s(source)
        
        # 转换阶段
        transform_tasks = []
        
        if transformations.get('filter_threshold'):
            transform_tasks.append(filter_data.s(transformations['filter_threshold']))
        
        if transformations.get('sort_desc'):
            transform_tasks.append(sort_data.s(transformations['sort_desc']))
        
        # 构建转换链
        if transform_tasks:
            transform_chain = chain(extract_task, *transform_tasks)
        else:
            transform_chain = extract_task
        
        # 加载阶段（并行执行多个输出任务）
        def load_phase(processed_data):
            load_tasks = []
            
            # 保存到数据库
            if output_config.get('database'):
                load_tasks.append(save_to_database.s(processed_data, output_config['database']))
            
            # 创建备份
            if output_config.get('backup_location'):
                load_tasks.append(backup_data.s(processed_data, output_config['backup_location']))
            
            # 发送通知
            if output_config.get('notify_channels'):
                load_tasks.append(send_notification.s(
                    "ETL流程完成",
                    output_config['notify_channels']
                ))
            
            return group(load_tasks) if load_tasks else []
        
        # 完整ETL工作流
        workflow = chain(
            transform_chain,
            load_phase
        )
        
        result = workflow.apply_async()
        workflow_result = workflow_manager.register_workflow(
            "comprehensive_etl_workflow",
            [result.id]
        )
        
        return result, workflow_result
