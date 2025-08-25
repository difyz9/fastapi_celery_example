# quick_test.py - 快速任务测试（异步）
from celery_app import app
from tasks.math_tasks import add, multiply, divide
from tasks.data_tasks import fetch_data, filter_data
from tasks.io_tasks import send_email
from celery import chain

def submit_tasks():
    """快速提交任务，不等待结果"""
    print("🚀 快速提交Celery任务...")
    print("=" * 40)
    
    # 1. 简单数学任务
    print("1️⃣ 提交数学任务 (5 + 3)...")
    result1 = add.delay(5, 3)
    print(f"   任务ID: {result1.id}")
    
    # 2. 任务链
    print("\n2️⃣ 提交任务链 (10+5)*2/3...")
    workflow = chain(
        add.s(10, 5),      # 15
        multiply.s(2),     # 30
        divide.s(3)        # 10
    )
    result2 = workflow.apply_async()
    print(f"   任务链ID: {result2.id}")
    
    # 3. 数据处理任务
    print("\n3️⃣ 提交数据处理任务...")
    data_workflow = chain(
        fetch_data.s("test"),    # [1,2,3,4,5]
        filter_data.s(2)         # [3,4,5]
    )
    result3 = data_workflow.apply_async()
    print(f"   数据任务ID: {result3.id}")
    
    # 4. IO任务
    print("\n4️⃣ 提交邮件发送任务...")
    result4 = send_email.delay("admin@example.com", "测试邮件", "任务执行测试")
    print(f"   邮件任务ID: {result4.id}")
    
    print("\n" + "=" * 40)
    print("✅ 所有任务已提交到队列！")
    print("\n📋 监控命令:")
    print("   celery -A celery_app inspect active    # 查看正在执行的任务")
    print("   celery -A celery_app inspect stats     # 查看统计信息")
    print("   celery -A celery_app inspect reserved  # 查看等待执行的任务")
    
    return [result1, result2, result3, result4]

if __name__ == "__main__":
    submit_tasks()
