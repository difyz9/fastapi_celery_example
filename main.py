# main.py - 标准化的主程序
from celery import chain
from workflows.data_workflow import create_math_workflow, create_data_processing_workflow, create_comprehensive_workflow
from workflows.workflow_manager import StandardWorkflows, workflow_manager
from tasks.math_tasks import add, multiply, divide
from tasks.data_tasks import fetch_data, filter_data, calculate_statistics
from tasks.io_tasks import send_email, generate_report
from config import AppConfig
import time

class TaskChainRunner:
    """任务链运行器"""
    
    def __init__(self):
        self.results = []
    
    def execute_simple_chain(self):
        """执行简单数学任务链"""
        print("🧮 执行简单数学任务链 (10+5)*2/3...")
        
        workflow = chain(
            add.s(10, 5),      # 10 + 5 = 15
            multiply.s(2),     # 15 * 2 = 30
            divide.s(3)        # 30 / 3 = 10
        )
        
        result = workflow.apply_async()
        self.results.append(("simple_math_chain", result))
        print(f"✅ 任务链已启动，ID: {result.id}")
        return result
    
    def execute_standard_math_workflow(self):
        """执行标准数学工作流"""
        print("\n🔢 执行标准数学工作流 (5+3)*4...")
        
        result, workflow_result = StandardWorkflows.math_calculation_chain(5, 3, 4)
        self.results.append(("standard_math_workflow", result))
        
        print(f"✅ 标准工作流已启动")
        print(f"   工作流ID: {workflow_result.workflow_id}")
        print(f"   任务ID: {result.id}")
        return result, workflow_result
    
    def execute_data_processing_workflow(self):
        """执行数据处理工作流"""
        print("\n📊 执行数据处理工作流...")
        
        result, workflow_result = StandardWorkflows.data_processing_pipeline("test", 2, 3)
        self.results.append(("data_processing_workflow", result))
        
        print(f"✅ 数据处理工作流已启动")
        print(f"   工作流ID: {workflow_result.workflow_id}")
        print(f"   任务ID: {result.id}")
        return result, workflow_result
    
    def execute_report_generation_workflow(self):
        """执行报告生成工作流"""
        print("\n📋 执行报告生成工作流...")
        
        recipients = ["admin@example.com", "manager@example.com"]
        result, workflow_result = StandardWorkflows.report_generation_workflow(
            "sample", "statistical", recipients
        )
        self.results.append(("report_generation_workflow", result))
        
        print(f"✅ 报告生成工作流已启动")
        print(f"   工作流ID: {workflow_result.workflow_id}")
        print(f"   收件人: {', '.join(recipients)}")
        print(f"   任务ID: {result.id}")
        return result, workflow_result
    
    def execute_etl_workflow(self):
        """执行ETL工作流"""
        print("\n🔄 执行ETL工作流...")
        
        transformations = {
            'filter_threshold': 1,
            'sort_desc': True
        }
        
        output_config = {
            'database': 'analytics_db',
            'backup_location': '/backup/etl_data',
            'notify_channels': ['email', 'slack']
        }
        
        result, workflow_result = StandardWorkflows.comprehensive_etl_workflow(
            "demo", transformations, output_config
        )
        self.results.append(("etl_workflow", result))
        
        print(f"✅ ETL工作流已启动")
        print(f"   工作流ID: {workflow_result.workflow_id}")
        print(f"   数据源: demo")
        print(f"   任务ID: {result.id}")
        return result, workflow_result
    
    def execute_mixed_workflow(self):
        """执行混合工作流"""
        print("\n🔀 执行混合工作流（数学+通知）...")
        
        workflow = chain(
            add.s(8, 7),        # 8 + 7 = 15
            multiply.s(3),      # 15 * 3 = 45
            send_email.s("admin@example.com", "计算结果通知", "数学计算已完成")
        )
        
        result = workflow.apply_async()
        self.results.append(("mixed_workflow", result))
        print(f"✅ 混合工作流已启动，ID: {result.id}")
        return result
    
    def show_monitoring_info(self):
        """显示监控信息"""
        print("\n" + "="*60)
        print("📊 监控和管理命令:")
        print("="*60)
        print("🔍 查看任务状态:")
        print("   python cli.py task active              # 查看活跃任务")
        print("   python cli.py task list                # 列出所有注册任务")
        print("   python cli.py worker status            # 查看Worker状态")
        
        print("\n📋 工作流管理:")
        print("   python cli.py workflow list            # 列出工作流")
        print("   python cli.py workflow math 10 5 2     # 执行数学工作流")
        print("   python cli.py workflow data test 2 3   # 执行数据工作流")
        
        print("\n🌸 启动监控界面:")
        print("   python cli.py monitor flower           # 启动Flower监控")
        print("   # 访问 http://localhost:5555")
        
        print("\n🔧 Celery原生命令:")
        print("   celery -A celery_app inspect active    # 查看活跃任务")
        print("   celery -A celery_app inspect stats     # 查看统计信息")
        print("   celery -A celery_app inspect reserved  # 查看等待任务")
    
    def get_workflow_summary(self):
        """获取工作流执行摘要"""
        print(f"\n📈 执行摘要:")
        print(f"   总共提交了 {len(self.results)} 个工作流")
        
        workflows = workflow_manager.list_workflows()
        print(f"   工作流管理器中记录了 {len(workflows)} 个工作流")
        
        for workflow in workflows[-3:]:  # 显示最近3个
            print(f"   🔸 {workflow.workflow_id} ({workflow.workflow_type})")

def main():
    """主函数"""
    print(f"🚀 {AppConfig.APP_NAME} - 任务链系统")
    print("="*60)
    print(f"环境: {AppConfig.ENVIRONMENT}")
    print(f"调试模式: {AppConfig.DEBUG}")
    print("="*60)
    
    # 创建运行器
    runner = TaskChainRunner()
    
    try:
        # 执行各种工作流
        runner.execute_simple_chain()
        time.sleep(0.5)  # 避免任务ID冲突
        
        runner.execute_standard_math_workflow()
        time.sleep(0.5)
        
        runner.execute_data_processing_workflow()
        time.sleep(0.5)
        
        runner.execute_report_generation_workflow()
        time.sleep(0.5)
        
        runner.execute_etl_workflow()
        time.sleep(0.5)
        
        runner.execute_mixed_workflow()
        
        # 显示摘要和监控信息
        runner.get_workflow_summary()
        runner.show_monitoring_info()
        
        print("\n✨ 所有任务已成功提交到队列！")
        
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)