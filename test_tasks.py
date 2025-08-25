# test_tasks.py - 完整的任务测试脚本
from celery_app import app
from celery import chain, group, chord
import time

def test_simple_math():
    """测试简单数学任务"""
    print("🧮 测试数学任务...")
    
    # 获取注册的任务
    add_task = app.tasks.get('math.add')
    if not add_task:
        print("❌ 找不到 math.add 任务")
        return None
    
    # 测试单个任务
    result = add_task.delay(5, 3)
    print(f"📝 加法任务 (5+3) - 任务ID: {result.id}")
    
    # 等待结果 (同步获取，仅用于演示)
    try:
        final_result = result.get(timeout=10)
        print(f"✅ 结果: {final_result}")
        return result
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_task_chain():
    """测试任务链"""
    print("\n🔗 测试任务链...")
    
    # 获取任务
    add_task = app.tasks.get('math.add')
    multiply_task = app.tasks.get('math.multiply')
    divide_task = app.tasks.get('math.divide')
    
    if not all([add_task, multiply_task, divide_task]):
        print("❌ 找不到必要的数学任务")
        return None
    
    # 创建任务链: 10 + 5 = 15, 15 * 2 = 30, 30 / 3 = 10
    workflow = chain(
        add_task.s(10, 5),      # 10 + 5 = 15
        multiply_task.s(2),     # 15 * 2 = 30  
        divide_task.s(3)        # 30 / 3 = 10
    )
    
    result = workflow.apply_async()
    print(f"📝 任务链已启动 - 任务ID: {result.id}")
    
    # 等待结果
    try:
        final_result = result.get(timeout=15)
        print(f"✅ 最终结果: {final_result}")
        return result
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_data_workflow():
    """测试数据处理工作流"""
    print("\n📊 测试数据处理工作流...")
    
    # 获取任务
    fetch_data_task = app.tasks.get('data.fetch_data')
    filter_data_task = app.tasks.get('data.filter_data')
    
    if not all([fetch_data_task, filter_data_task]):
        print("❌ 找不到必要的数据处理任务")
        return None
    
    # 创建数据处理链
    workflow = chain(
        fetch_data_task.s("test"),    # 获取测试数据 [1,2,3,4,5]
        filter_data_task.s(2)         # 过滤大于2的数据 [3,4,5]
    )
    
    result = workflow.apply_async()
    print(f"📝 数据工作流已启动 - 任务ID: {result.id}")
    
    try:
        final_result = result.get(timeout=15)
        print(f"✅ 过滤后的数据: {final_result}")
        return result
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_parallel_tasks():
    """测试并行任务组"""
    print("\n🚀 测试并行任务组...")
    
    # 获取数学任务
    add_task = app.tasks.get('math.add')
    multiply_task = app.tasks.get('math.multiply')
    subtract_task = app.tasks.get('math.subtract')
    
    if not all([add_task, multiply_task, subtract_task]):
        print("❌ 找不到必要的数学任务")
        return None
    
    # 创建并行任务组
    parallel_group = group(
        add_task.s(10, 5),        # 10 + 5 = 15
        multiply_task.s(4, 3),    # 4 * 3 = 12
        subtract_task.s(20, 8)    # 20 - 8 = 12
    )
    
    result = parallel_group.apply_async()
    print(f"📝 并行任务组已启动 - 任务ID: {result.id}")
    
    try:
        final_results = result.get(timeout=15)
        print(f"✅ 并行结果: {final_results}")
        return result
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_mixed_workflow():
    """测试混合工作流"""
    print("\n🔀 测试混合工作流...")
    
    # 获取任务
    add_task = app.tasks.get('math.add')
    multiply_task = app.tasks.get('math.multiply')
    send_email_task = app.tasks.get('io.send_email')
    
    if not all([add_task, multiply_task, send_email_task]):
        print("❌ 找不到必要的任务")
        return None
    
    # 混合数学计算和IO任务
    workflow = chain(
        add_task.s(7, 3),        # 7 + 3 = 10
        multiply_task.s(5),      # 10 * 5 = 50
        send_email_task.s("admin@example.com", "计算完成")
    )
    
    result = workflow.apply_async()
    print(f"📝 混合工作流已启动 - 任务ID: {result.id}")
    
    try:
        final_result = result.get(timeout=15)
        print(f"✅ 邮件发送结果: {final_result}")
        return result
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_async_execution():
    """测试异步执行（不等待结果）"""
    print("\n⚡ 测试异步执行...")
    
    # 获取任务
    power_task = app.tasks.get('math.power')
    sqrt_task = app.tasks.get('math.sqrt')
    
    if not all([power_task, sqrt_task]):
        print("❌ 找不到必要的数学任务")
        return None
    
    # 异步提交任务
    result1 = power_task.delay(3, 4)  # 3^4 = 81
    result2 = sqrt_task.delay(64)     # √64 = 8
    
    print(f"📝 异步任务已提交:")
    print(f"   - 幂运算任务ID: {result1.id}")
    print(f"   - 开方任务ID: {result2.id}")
    print("🔄 任务在后台执行中...")
    
    return [result1, result2]

def check_task_status(result):
    """检查任务状态"""
    if result is None:
        return
    
    print(f"\n📊 任务状态检查 - ID: {result.id}")
    print(f"   状态: {result.status}")
    
    if result.ready():
        try:
            print(f"   结果: {result.result}")
        except Exception as e:
            print(f"   错误: {e}")
    else:
        print("   任务仍在执行中...")

def main():
    """主测试函数"""
    print("🚀 开始测试 Celery 任务执行...")
    print("=" * 60)
    
    # 检查任务注册情况
    print("📋 已注册的任务:")
    user_tasks = [task for task in app.tasks.keys() if not task.startswith('celery.')]
    for task in sorted(user_tasks):
        print(f"  - {task}")
    print(f"\n总共注册了 {len(user_tasks)} 个任务")
    print()
    
    # 运行各种测试
    results = []
    
    # 1. 基础测试
    result1 = test_simple_math()
    if result1:
        results.append(result1)
    
    # 2. 任务链测试
    result2 = test_task_chain()
    if result2:
        results.append(result2)
    
    # 3. 数据工作流测试
    result3 = test_data_workflow()
    if result3:
        results.append(result3)
    
    # 4. 并行任务测试
    result4 = test_parallel_tasks()
    if result4:
        results.append(result4)
    
    # 5. 混合工作流测试
    result5 = test_mixed_workflow()
    if result5:
        results.append(result5)
    
    # 6. 异步执行测试
    async_results = test_async_execution()
    if async_results:
        results.extend(async_results)
    
    print("\n" + "=" * 60)
    print("✨ 测试完成！")
    
    # 显示所有任务状态
    if results:
        print(f"\n📊 任务状态汇总 (共 {len(results)} 个任务):")
        for i, result in enumerate(results, 1):
            if result:
                status = "✅ 完成" if result.ready() else "🔄 执行中"
                print(f"  {i}. 任务 {result.id}: {status}")
    
    print("\n💡 监控命令:")
    print("   celery -A celery_app inspect active    # 查看活跃任务")
    print("   celery -A celery_app inspect stats     # 查看统计信息")
    print("   celery -A celery_app inspect registered # 查看注册任务")

if __name__ == "__main__":
    main()
