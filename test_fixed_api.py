#!/usr/bin/env python3
# test_fixed_api.py - 测试修复后的数学API

import requests
import json
import time

def test_math_api():
    """测试数学API端点"""
    
    base_url = "http://localhost:8000"
    
    print("🧮 测试数学任务API")
    print("=" * 50)
    
    # 1. 测试获取数学链信息
    print("1. 获取可用的数学任务链...")
    try:
        response = requests.get(f"{base_url}/math/chains")
        if response.status_code == 200:
            chains = response.json()
            print("✅ 获取数学链成功")
            print(f"   可用链数量: {len(chains.get('math_chains', {}))}")
            for name, info in chains.get('math_chains', {}).items():
                print(f"   - {name}: {info['description']}")
        else:
            print(f"❌ 获取数学链失败: {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False
    
    # 2. 测试提交数学任务
    print("\n2. 提交数学任务...")
    test_cases = [
        {"a": 10, "b": 5, "operation_chain": "add_multiply_divide"},
        {"a": 8, "b": 3, "operation_chain": "power_sqrt"},
        {"a": 15, "b": 7, "operation_chain": "complex_math"}
    ]
    
    submitted_tasks = []
    
    for i, test_data in enumerate(test_cases, 1):
        try:
            print(f"   测试案例 {i}: {test_data}")
            response = requests.post(f"{base_url}/math/submit", json=test_data)
            
            if response.status_code == 200:
                result = response.json()
                task_id = result["task_id"]
                submitted_tasks.append(task_id)
                print(f"   ✅ 任务提交成功")
                print(f"      任务ID: {task_id}")
                print(f"      链类型: {test_data['operation_chain']}")
                print(f"      描述: {result.get('message', 'N/A')}")
            else:
                print(f"   ❌ 任务提交失败: {response.status_code}")
                print(f"      错误: {response.text}")
        except Exception as e:
            print(f"   ❌ 提交失败: {e}")
    
    # 3. 测试查询任务状态
    if submitted_tasks:
        print(f"\n3. 查询任务状态...")
        time.sleep(2)  # 等待任务执行
        
        for task_id in submitted_tasks:
            try:
                response = requests.get(f"{base_url}/tasks/{task_id}/status")
                if response.status_code == 200:
                    status = response.json()
                    print(f"   任务 {task_id[:8]}... 状态: {status.get('status', 'unknown')}")
                    if status.get('status') == 'completed':
                        print(f"      ✅ 完成结果: {status.get('result', 'N/A')}")
                else:
                    print(f"   ❌ 查询失败: {response.status_code}")
            except Exception as e:
                print(f"   ❌ 查询错误: {e}")
    
    # 4. 测试获取任务列表
    print(f"\n4. 获取任务列表...")
    try:
        response = requests.get(f"{base_url}/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print(f"   ✅ 获取成功，共 {len(tasks.get('tasks', []))} 个任务")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 获取错误: {e}")
    
    print("\n🎉 测试完成!")
    return True

def main():
    """主函数"""
    print("🧪 数学API修复验证测试")
    print("确保以下服务正在运行:")
    print("1. Redis服务器")
    print("2. Celery Worker: celery -A celery_app worker --loglevel=info")
    print("3. FastAPI服务器: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print()
    
    input("按 Enter 键开始测试...")
    
    if test_math_api():
        print("\n✅ 所有测试通过！数学API修复成功。")
    else:
        print("\n❌ 部分测试失败，请检查服务状态。")

if __name__ == "__main__":
    main()
