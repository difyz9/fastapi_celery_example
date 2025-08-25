# test_modular_routes.py - 测试模块化路由结构
import requests
import json
from datetime import datetime

def test_modular_api():
    """测试模块化API路由"""
    print("🧪 测试模块化路由结构")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. 测试主API信息
        print("\n1️⃣ 测试主API信息...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API消息: {data['message']}")
            print(f"✅ 版本: {data['version']}")
            print(f"✅ 架构: {data['architecture']}")
            print("\n📍 端点结构:")
            for category, endpoints in data['endpoints'].items():
                print(f"  {category}:")
                for name, path in endpoints.items():
                    print(f"    - {name}: {path}")
        else:
            print(f"❌ 主API测试失败: {response.status_code}")
            return
        
        # 2. 测试数学任务路由
        print("\n2️⃣ 测试数学任务路由...")
        math_chains_response = requests.get(f"{base_url}/math/chains")
        if math_chains_response.status_code == 200:
            chains = math_chains_response.json()
            print(f"✅ 数学任务链数量: {len(chains.get('descriptions', {}))}")
            for name, desc in chains.get('descriptions', {}).items():
                print(f"    - {name}: {desc}")
        else:
            print(f"❌ 数学任务链获取失败: {math_chains_response.status_code}")
        
        # 3. 测试Bilibili路由
        print("\n3️⃣ 测试Bilibili任务路由...")
        bilibili_chains_response = requests.get(f"{base_url}/bilibili/chains")
        if bilibili_chains_response.status_code == 200:
            chains = bilibili_chains_response.json()
            print(f"✅ Bilibili任务链数量: {len(chains.get('descriptions', {}))}")
            for name, desc in chains.get('descriptions', {}).items():
                print(f"    - {name}: {desc}")
        else:
            print(f"❌ Bilibili任务链获取失败: {bilibili_chains_response.status_code}")
        
        # 4. 测试任务管理路由
        print("\n4️⃣ 测试任务管理路由...")
        tasks_response = requests.get(f"{base_url}/tasks")
        if tasks_response.status_code == 200:
            tasks = tasks_response.json()
            print(f"✅ 任务列表获取成功")
            print(f"    总任务数: {tasks.get('total_tasks', 0)}")
        else:
            print(f"❌ 任务列表获取失败: {tasks_response.status_code}")
        
        # 5. 测试统计信息
        print("\n5️⃣ 测试统计信息...")
        stats_response = requests.get(f"{base_url}/tasks/statistics")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"✅ 统计信息获取成功")
            statistics = stats.get('statistics', {})
            for key, value in statistics.items():
                print(f"    {key}: {value}")
        else:
            print(f"❌ 统计信息获取失败: {stats_response.status_code}")
        
        # 6. 测试健康检查
        print("\n6️⃣ 测试健康检查...")
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code == 200:
            health = health_response.json()
            print(f"✅ 服务状态: {health['status']}")
            print(f"    组件:")
            for component, tech in health.get('components', {}).items():
                print(f"    - {component}: {tech}")
        else:
            print(f"❌ 健康检查失败: {health_response.status_code}")
        
        print(f"\n🎉 模块化路由测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败！请确保FastAPI服务器正在运行")
        print("   启动命令: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")

if __name__ == "__main__":
    print(f"🚀 模块化路由测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    test_modular_api()
