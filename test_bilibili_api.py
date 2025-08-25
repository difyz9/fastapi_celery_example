# test_bilibili_api.py - 测试Bilibili视频处理API
import requests
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def test_bilibili_video_submission():
    """测试Bilibili视频提交"""
    print("🧪 测试Bilibili视频处理API")
    print("=" * 50)
    
    # 测试数据
    video_data = {
        "title": "油管Flutter 大师班 - FULL FLUTTER COURSES",
        "aid": 1254761143,
        "bvid": "BV1AJ4m1P7MY",
        "cid": 1557321576,
        "author": "精选海外教程postcode",
        "currentPart": 6,
        "isCollection": True,
        "totalParts": 16,
        "url": "https://www.bilibili.com/video/BV1AJ4m1P7MY?p=6",
        "duration": 2997,
        "submittedAt": "2025-08-19T16:59:58.783Z",
        "source": "chrome_extension",
        "currentPlayTime": 1200.5
    }
    
    try:
        # 1. 提交Bilibili视频处理任务
        print("\n📤 1. 提交Bilibili视频处理任务...")
        submit_response = requests.post(
            f"{API_BASE_URL}/bilibili/submit",
            json=video_data,
            params={"chain_name": "video_processing_chain"}
        )
        
        if submit_response.status_code == 200:
            submit_result = submit_response.json()
            task_id = submit_result["task_id"]
            print(f"✅ 任务提交成功!")
            print(f"   任务ID: {task_id}")
            print(f"   状态: {submit_result['status']}")
            print(f"   描述: {submit_result['message']}")
        else:
            print(f"❌ 任务提交失败: {submit_response.status_code}")
            print(f"   错误: {submit_response.text}")
            return
        
        # 2. 查询任务状态
        print(f"\n🔍 2. 查询任务状态...")
        for i in range(10):  # 最多查询10次
            time.sleep(3)  # 等待3秒
            
            status_response = requests.get(f"{API_BASE_URL}/tasks/{task_id}/status")
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                print(f"   第{i+1}次查询 - 状态: {status_result['status']}")
                
                if status_result['status'] in ['completed', 'failed']:
                    break
            else:
                print(f"   查询失败: {status_response.status_code}")
        
        # 3. 获取最终结果
        print(f"\n📋 3. 获取最终结果...")
        result_response = requests.get(f"{API_BASE_URL}/tasks/{task_id}/result")
        
        if result_response.status_code == 200:
            result_data = result_response.json()
            print(f"✅ 任务完成状态: {result_data['status']}")
            
            if result_data['result']:
                print("📊 处理结果:")
                result = result_data['result']
                
                # 显示处理链结果
                if isinstance(result, dict):
                    task_name = result.get('task_name', 'Unknown')
                    print(f"   最后执行的任务: {task_name}")
                    
                    if 'upload_info' in result:
                        upload_info = result['upload_info']
                        print(f"   上传文件数: {upload_info.get('uploaded_files_count', 0)}")
                        print(f"   总大小: {upload_info.get('total_size', 'Unknown')}")
                    
                    if 'video_info' in result:
                        video_info = result['video_info']
                        print(f"   视频标题: {video_info.get('title', 'Unknown')}")
                        print(f"   视频BV号: {video_info.get('bvid', 'Unknown')}")
        else:
            print(f"❌ 获取结果失败: {result_response.status_code}")
        
        # 4. 查看可用的Bilibili处理链
        print(f"\n🔗 4. 查看可用的Bilibili处理链...")
        chains_response = requests.get(f"{API_BASE_URL}/bilibili/chains")
        
        if chains_response.status_code == 200:
            chains_data = chains_response.json()
            print("   可用的处理链:")
            for chain_name, chain_info in chains_data["descriptions"].items():
                print(f"   - {chain_name}: {chain_info}")
        
        # 5. 查看任务统计
        print(f"\n📈 5. 查看任务统计...")
        stats_response = requests.get(f"{API_BASE_URL}/tasks/statistics")
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("   任务统计:")
            stats = stats_data["statistics"]
            for key, value in stats.items():
                print(f"   - {key}: {value}")
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败！请确保:")
        print("   1. FastAPI服务器正在运行 (python server.py)")
        print("   2. Celery Worker正在运行 (celery -A celery_app worker --loglevel=info)")
        print("   3. Redis服务器正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")

def test_api_info():
    """测试API信息"""
    print("\n🌐 测试API信息...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            api_info = response.json()
            print(f"✅ API版本: {api_info['version']}")
            print(f"   架构: {api_info['architecture']}")
            print("   可用端点:")
            for endpoint, path in api_info['endpoints'].items():
                print(f"   - {endpoint}: {path}")
        else:
            print(f"❌ 获取API信息失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API信息查询失败: {e}")

if __name__ == "__main__":
    print(f"🚀 Bilibili视频处理API测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试API基本信息
    test_api_info()
    
    # 测试Bilibili视频处理
    test_bilibili_video_submission()
    
    print("\n✨ 测试完成!")
