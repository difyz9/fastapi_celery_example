# simple_test.py - 简单的任务执行测试（不等待结果）
from celery_app import app
import time

def test_simple_execution():
    """测试简单任务执行（异步）"""
    print("🧪 测试简单任务执行...")
    
    # 获取数学任务
    add_task = app.tasks.get('math.add')
    if not add_task:
        print("❌ 找不到 math.add 任务")
        return
    
    print(f"✅ 找到任务: {add_task.name}")
    
    # 异步提交任务（不等待结果）
    print("📤 提交加法任务 (10 + 5)...")
    result = add_task.delay(10, 5)
    print(f"📝 任务已提交 - ID: {result.id}")
    print(f"📊 任务状态: {result.status}")
    
    # 等待几秒钟看看状态变化
    for i in range(5):
        time.sleep(1)
        try:
            status = result.status
            print(f"⏰ {i+1}秒后状态: {status}")
            if status == 'SUCCESS':
                try:
                    result_value = result.result
                    print(f"✅ 任务完成！结果: {result_value}")
                    break
                except Exception as e:
                    print(f"⚠️ 获取结果时出错: {e}")
            elif status == 'FAILURE':
                print(f"❌ 任务失败: {result.result}")
                break
        except Exception as e:
            print(f"⚠️ 检查状态时出错: {e}")
    
    return result

def test_worker_connection():
    """测试worker连接"""
    print("\n🔗 测试worker连接...")
    
    try:
        # 检查活跃的workers
        inspect = app.control.inspect()
        stats = inspect.stats()
        active = inspect.active()
        
        if stats:
            print(f"📊 发现 {len(stats)} 个worker:")
            for worker, stat in stats.items():
                print(f"  - {worker}: {stat.get('pool', {}).get('processes', 'N/A')} 进程")
        else:
            print("❌ 没有发现活跃的worker")
            
        if active:
            print(f"🔄 活跃任务:")
            for worker, tasks in active.items():
                print(f"  - {worker}: {len(tasks)} 个任务")
        else:
            print("📝 没有活跃任务")
            
    except Exception as e:
        print(f"❌ 检查worker时出错: {e}")

if __name__ == "__main__":
    print("🚀 开始简单测试...")
    print("=" * 50)
    
    test_worker_connection()
    result = test_simple_execution()
    
    print("\n" + "=" * 50)
    print("✨ 测试完成！")
    
    if result:
        print(f"\n💡 要查看任务详情，运行:")
        print(f"   python -c \"from celery_app import app; r = app.AsyncResult('{result.id}'); print(f'状态: {{r.status}}'); print(f'结果: {{r.result if r.ready() else \\\"未完成\\\"}}')\"")
