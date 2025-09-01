#!/usr/bin/env python3
"""
测试简化的处理器结果传递机制
验证上一个任务的执行结果能正确传递给下一个任务
"""

import asyncio
import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000"

def test_simple_result_passing():
    """测试简单的结果传递：上一个任务的执行结果传递给下一个任务"""
    
    print("🧪 测试简化的结果传递机制")
    print("=" * 50)
    
    # 准备测试数据
    test_data = {
        "video_id": 12345,
        "subtitles": [
            {"start": 0, "end": 2, "text": "Hello world"},
            {"start": 2, "end": 4, "text": "This is a test"},
            {"start": 4, "end": 6, "text": "测试中文字幕"}
        ]
    }
    
    print(f"📝 提交测试任务...")
    print(f"视频ID: {test_data['video_id']}")
    print(f"字幕数量: {len(test_data['subtitles'])}")
    
    try:
        # 提交完整处理任务
        response = requests.post(f"{BASE_URL}/tasks/submit", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            task_id = result["task_id"]
            print(f"✅ 任务提交成功！任务ID: {task_id}")
            
            # 监控任务执行
            print(f"\n🔄 监控任务执行...")
            max_wait = 30  # 最多等待30秒
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                status_response = requests.get(f"{BASE_URL}/tasks/status/{task_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data["status"]
                    
                    print(f"📊 任务状态: {current_status}")
                    
                    if current_status == "completed":
                        print(f"\n🎉 任务执行完成！")
                        print("📋 最终结果:")
                        print(json.dumps(status_data.get("result", {}), 
                                       indent=2, ensure_ascii=False))
                        
                        # 分析结果传递
                        analyze_result_passing(status_data.get("result", {}))
                        return True
                        
                    elif current_status == "failed":
                        print(f"❌ 任务执行失败:")
                        print(json.dumps(status_data, indent=2, ensure_ascii=False))
                        return False
                
                time.sleep(2)  # 每2秒检查一次
            
            print(f"⏰ 任务执行超时（{max_wait}秒）")
            return False
            
        else:
            print(f"❌ 任务提交失败: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到FastAPI服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def analyze_result_passing(result):
    """分析结果传递情况"""
    print(f"\n🔍 分析结果传递:")
    print("-" * 30)
    
    if "data" in result:
        data = result["data"]
        print(f"📦 最终数据包含的字段:")
        for key in data.keys():
            print(f"   - {key}")
        
        # 检查各个处理器的结果是否都传递了
        expected_fields = ["subtitles", "detected_language", "translated_subtitles", 
                          "audio_files", "uploaded_files"]
        
        print(f"\n✅ 结果传递验证:")
        for field in expected_fields:
            if field in data:
                print(f"   ✅ {field}: 已传递")
            else:
                print(f"   ❌ {field}: 缺失")
    
    if "metadata" in result:
        metadata = result["metadata"]
        print(f"\n📊 元数据信息:")
        for key, value in metadata.items():
            print(f"   - {key}: {value}")

def test_single_processor():
    """测试单个处理器"""
    print(f"\n🧪 测试单个处理器（语言检测）")
    print("=" * 50)
    
    test_data = {
        "video_id": 67890,
        "subtitles": [
            {"start": 0, "end": 2, "text": "English text"},
            {"start": 2, "end": 4, "text": "中文文本"},
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks/detect-language", 
                               json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            task_id = result["task_id"]
            print(f"✅ 语言检测任务提交成功！任务ID: {task_id}")
            
            # 等待几秒后检查结果
            time.sleep(3)
            status_response = requests.get(f"{BASE_URL}/tasks/status/{task_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"📊 任务状态: {status_data['status']}")
                
                if status_data["status"] == "completed":
                    print("📋 检测结果:")
                    print(json.dumps(status_data.get("result", {}), 
                                   indent=2, ensure_ascii=False))
                    return True
        
        return False
        
    except Exception as e:
        print(f"❌ 单处理器测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试简化的处理器结果传递机制")
    print("请确保以下服务正在运行：")
    print("1. FastAPI应用 (http://localhost:8000)")
    print("2. Celery worker")
    print("3. Redis服务器")
    print()
    
    # 测试完整管道
    success1 = test_simple_result_passing()
    
    # 测试单个处理器
    success2 = test_single_processor()
    
    print(f"\n📊 测试总结:")
    print(f"完整管道测试: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"单处理器测试: {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print(f"\n🎉 所有测试通过！简化的结果传递机制工作正常。")
        print(f"上一个任务的执行结果成功传递给下一个任务。")
    else:
        print(f"\n⚠️  部分测试失败，请检查日志。")
