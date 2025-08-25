#!/bin/bash

# bilibili_test.sh - Bilibili视频处理API的curl测试脚本

API_BASE="http://localhost:8000"

echo "🚀 Bilibili视频处理API测试"
echo "================================"

# 检查API是否运行
echo "🔍 1. 检查API状态..."
curl -s "$API_BASE/" | jq '.' 2>/dev/null || echo "API可能未启动或jq未安装"

echo -e "\n📋 2. 查看可用的Bilibili处理链..."
curl -s "$API_BASE/bilibili/chains" | jq '.' 2>/dev/null || echo "获取处理链信息失败"

echo -e "\n📤 3. 提交Bilibili视频处理任务..."

# Bilibili视频数据
VIDEO_DATA='{
  "title": "油管Flutter 大师班 - FULL FLUTTER COURSES",
  "aid": 1254761143,
  "bvid": "BV1AJ4m1P7MY",
  "cid": 1557321576,
  "author": "精选海外教程postcode",
  "currentPart": 6,
  "isCollection": true,
  "totalParts": 16,
  "url": "https://www.bilibili.com/video/BV1AJ4m1P7MY?p=6",
  "duration": 2997,
  "submittedAt": "2025-08-19T16:59:58.783Z",
  "source": "chrome_extension",
  "currentPlayTime": 1200.5
}'

# 提交任务
SUBMIT_RESPONSE=$(curl -s -X POST "$API_BASE/bilibili/submit?chain_name=video_processing_chain" \
  -H "Content-Type: application/json" \
  -d "$VIDEO_DATA")

echo "提交响应:"
echo "$SUBMIT_RESPONSE" | jq '.' 2>/dev/null || echo "$SUBMIT_RESPONSE"

# 提取任务ID
TASK_ID=$(echo "$SUBMIT_RESPONSE" | jq -r '.task_id' 2>/dev/null)

if [ "$TASK_ID" != "null" ] && [ "$TASK_ID" != "" ]; then
    echo -e "\n✅ 任务已提交，ID: $TASK_ID"
    
    echo -e "\n🔍 4. 查询任务状态 (每3秒查询一次，最多10次)..."
    for i in {1..10}; do
        echo "第 $i 次查询..."
        STATUS_RESPONSE=$(curl -s "$API_BASE/tasks/$TASK_ID/status")
        STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status' 2>/dev/null)
        
        echo "状态: $STATUS"
        
        if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
            echo "任务已完成，状态: $STATUS"
            break
        fi
        
        if [ $i -lt 10 ]; then
            echo "等待3秒..."
            sleep 3
        fi
    done
    
    echo -e "\n📊 5. 获取最终结果..."
    curl -s "$API_BASE/tasks/$TASK_ID/result" | jq '.' 2>/dev/null || echo "获取结果失败"
    
else
    echo "❌ 无法提取任务ID，任务提交可能失败"
fi

echo -e "\n📈 6. 查看任务统计..."
curl -s "$API_BASE/tasks/statistics" | jq '.' 2>/dev/null || echo "获取统计信息失败"

echo -e "\n🔗 7. 查看所有可用任务链..."
curl -s "$API_BASE/chains" | jq '.' 2>/dev/null || echo "获取任务链信息失败"

echo -e "\n✨ 测试完成!"
echo -e "\n💡 提示:"
echo "- 确保FastAPI服务器正在运行: python server.py"
echo "- 确保Celery Worker正在运行: celery -A celery_app worker --loglevel=info"
echo "- 确保Redis服务器正在运行: brew services start redis"
echo "- 安装jq以获得更好的JSON格式化: brew install jq"
