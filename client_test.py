# client_test.py - 客户端测试脚本
from celery_app import app
from celery import chain, group
import time

def quick_test():
    """快速测试任务执行"""
    print("🚀 快速任务测试开始...")
    
    # 测试单个任务
    print("\n1️⃣ 测试单个加法任务:")
    result = app.send_task('math.add', args=[15, 25])
    print(f"   任务ID: {result.id}")
    final_result = result.get(timeout=10)
    print(f"   结果: {final_result}")
    
    # 测试任务链
    print("\n2️⃣ 测试任务链:")
    workflow = chain(
        app.signature('math.add', args=[10, 20]),      # 30
        app.signature('math.multiply', args=[3]),      # 90
        app.signature('math.divide', args=[2])         # 45
    )
    
    result = workflow.apply_async()
    print(f"   任务链ID: {result.id}")
    final_result = result.get(timeout=15)
    print(f"   最终结果: {final_result}")
    
    # 测试数据处理
    print("\n3️⃣ 测试数据处理:")
    workflow = chain(
        app.signature('data.fetch_data', args=['test']),
        app.signature('data.filter_data', args=[5])
    )
    
    result = workflow.apply_async()
    print(f"   数据处理ID: {result.id}")
    final_result = result.get(timeout=15)
    print(f"   过滤结果: {final_result}")
    
    # 测试并行任务
    print("\n4️⃣ 测试并行任务:")
    parallel_tasks = group(
        app.signature('math.power', args=[2, 8]),      # 256
        app.signature('math.sqrt', args=[144]),        # 12
        app.signature('math.add', args=[100, 200])     # 300
    )
    
    result = parallel_tasks.apply_async()
    print(f"   并行任务ID: {result.id}")
    final_results = result.get(timeout=15)
    print(f"   并行结果: {final_results}")
    
    # 测试IO任务
    print("\n5️⃣ 测试IO任务:")
    result = app.send_task('io.send_email', args=['test@example.com', '测试邮件', '这是一封测试邮件'])
    print(f"   邮件任务ID: {result.id}")
    final_result = result.get(timeout=10)
    print(f"   邮件结果: {final_result}")
    
    print("\n✅ 所有测试完成!")

if __name__ == "__main__":
    quick_test()
