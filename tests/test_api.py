"""
API接口测试
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "视频处理任务系统"


def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_submit_task():
    """测试任务提交"""
    task_data = {
        "video_id": 123456,
        "subtitles": [
            {
                "start_time": 0.0,
                "end_time": 5.5,
                "text": "测试字幕",
                "language": "zh-CN"
            }
        ],
        "platform": "bilibili",
        "task_type": "detect"
    }
    
    response = client.post("/api/v1/tasks/submit", json=task_data)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["video_id"] == 123456


def test_sync_task():
    """测试同步任务执行"""
    task_data = {
        "video_id": 789012,
        "subtitles": [
            {
                "start_time": 0.0,
                "end_time": 3.0,
                "text": "Hello world",
                "language": "en"
            }
        ],
        "platform": "bilibili",
        "task_type": "detect"
    }
    
    response = client.post("/api/v1/tasks/sync", json=task_data)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert "result" in data
    assert data["status"] == "success"


def test_task_stats():
    """测试任务统计"""
    response = client.get("/api/v1/tasks/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_tasks" in data
    assert "status_distribution" in data


def test_system_info():
    """测试系统信息"""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "celery" in data
    assert "redis" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
