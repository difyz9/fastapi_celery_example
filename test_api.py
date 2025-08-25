# test_api.py - API测试客户端
import requests
import time
import json

# API基础URL
BASE_URL = "http://localhost:8000"

def test_api():
    """测试API功能"""
    print("🚀 开始测试API...")
    
    # 1. 测试根路径
    print("\n1️⃣ 测试API信息:")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 2. 获取可用任务链
    print("\n2️⃣ 获取可用任务链:")
    response = requests.get(f"{BASE_URL}/chains")
    print(f"可用任务链: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 3. 提交任务
    print("\n3️⃣ 提交数学运算任务:")
    task_data = {
        "a": 10,
        "b": 5,
        "operation_chain": "add_multiply_divide"
    }
    
    response = requests.post(f"{BASE_URL}/submit", json=task_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        task_info = response.json()
        print(f"任务提交成功: {json.dumps(task_info, indent=2, ensure_ascii=False)}")
        task_id = task_info["task_id"]
        
        # 4. 查询任务状态
        print("\n4️⃣ 查询任务状态:")
        for i in range(5):  # 最多查询5次
            print(f"第 {i+1} 次查询...")
            response = requests.get(f"{BASE_URL}/status/{task_id}")
            
            if response.status_code == 200:
                status_info = response.json()
                print(f"任务状态: {json.dumps(status_info, indent=2, ensure_ascii=False)}")
                
                if status_info["status"] in ["completed", "failed"]:
                    break
                    
            time.sleep(2)  # 等待2秒再查询
    
    # 5. 提交其他类型的任务
    print("\n5️⃣ 提交幂运算任务:")
    task_data = {
        "a": 3,
        "b": 4,
        "operation_chain": "power_sqrt"
    }
    
    response = requests.post(f"{BASE_URL}/submit", json=task_data)
    if response.status_code == 200:
        task_info = response.json()
        print(f"幂运算任务: {json.dumps(task_info, indent=2, ensure_ascii=False)}")
    
    # 6. 提交复杂数学运算
    print("\n6️⃣ 提交复杂数学运算:")
    task_data = {
        "a": 20,
        "b": 8,
        "operation_chain": "complex_math"
    }
    
    response = requests.post(f"{BASE_URL}/submit", json=task_data)
    if response.status_code == 200:
        task_info = response.json()
        print(f"复杂运算任务: {json.dumps(task_info, indent=2, ensure_ascii=False)}")
    
    # 7. 获取任务列表
    print("\n7️⃣ 获取任务列表:")
    time.sleep(3)  # 等待任务执行
    response = requests.get(f"{BASE_URL}/tasks")
    if response.status_code == 200:
        tasks_info = response.json()
        print(f"任务列表: {json.dumps(tasks_info, indent=2, ensure_ascii=False)}")
    
    print("\n✅ API测试完成!")

def test_error_cases():
    """测试错误情况"""
    print("\n🔍 测试错误情况:")
    
    # 测试无效的任务链
    print("\n1️⃣ 测试无效任务链:")
    task_data = {
        "a": 10,
        "b": 5,
        "operation_chain": "invalid_chain"
    }
    
    response = requests.post(f"{BASE_URL}/submit", json=task_data)
    print(f"状态码: {response.status_code}")
    print(f"错误信息: {response.json()}")
    
    # 测试获取不存在的任务
    print("\n2️⃣ 测试获取不存在的任务:")
    response = requests.get(f"{BASE_URL}/status/non-existent-task")
    print(f"状态码: {response.status_code}")
    print(f"错误信息: {response.json()}")

if __name__ == "__main__":
    try:
        test_api()
        test_error_cases()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请确保API服务器正在运行")
        print("   启动命令: python api.py")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
