#!/usr/bin/env python3
"""
直接测试Bilibili任务链执行
"""
import asyncio
from celery_app import app
from tasks.bilibili_tasks import download_subtitle
from app.services.chain_service import ChainService

def test_bilibili_task_direct():
    """直接测试Bilibili任务"""
    print("🧪 开始直接测试Bilibili任务链...")
    
    # 测试数据
    video_info = {
        "bvid": "BV1test_direct",
        "title": "直接测试视频",
        "author": "直接测试UP主",
        "aid": 1234567890,
        "cid": 9876543210,
        "duration": 300
    }
    
    try:
        # 测试单个任务
        print("📤 测试单个任务: download_subtitle...")
        result1 = download_subtitle.delay(video_info)
        print(f"✅ 单个任务已提交，ID: {result1.id}")
        
        # 测试任务链
        print("📤 测试完整任务链...")
        chain_service = ChainService()
        task_chain = chain_service.create_bilibili_chain("video_processing_chain", video_info)
        result2 = task_chain.apply_async()
        print(f"✅ 任务链已提交，ID: {result2.id}")
        print(f"📊 任务链状态: {result2.state}")
        
        # 等待结果（最多等待30秒）
        print("⏳ 等待任务链执行结果...")
        try:
            final_result = result2.get(timeout=30)
            print(f"🎉 任务链执行完成！")
            print(f"📋 执行结果: {final_result}")
        except Exception as e:
            print(f"❌ 等待结果时出错: {e}")
            print(f"📊 当前任务状态: {result2.state}")
            print(f"📋 任务信息: {result2.info}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_bilibili_task_direct()
