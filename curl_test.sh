#!/bin/bash
# curl_test.sh - 使用curl测试API的脚本

echo "🚀 开始使用curl测试API..."
echo "=" * 50

# API基础URL
API_URL="http://localhost:8000"

echo "1️⃣ 获取API信息:"
curl -s -X GET "$API_URL/" | python3 -m json.tool
echo

echo "2️⃣ 获取可用任务链:"
curl -s -X GET "$API_URL/chains" | python3 -m json.tool
echo

echo "3️⃣ 提交数学运算任务 (10 + 5):"
RESPONSE=$(curl -s -X POST "$API_URL/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "a": 10,
    "b": 5,
    "operation_chain": "add_multiply_divide"
  }')

echo "$RESPONSE" | python3 -m json.tool

# 提取任务ID
TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['task_id'])" 2>/dev/null)

if [ ! -z "$TASK_ID" ]; then
    echo
    echo "4️⃣ 查询任务状态 (任务ID: $TASK_ID):"
    
    # 等待2秒让任务执行
    echo "⏳ 等待任务执行..."
    sleep 2
    
    curl -s -X GET "$API_URL/status/$TASK_ID" | python3 -m json.tool
    echo
    
    # 再次查询确保任务完成
    echo "5️⃣ 再次查询任务状态:"
    sleep 3
    curl -s -X GET "$API_URL/status/$TASK_ID" | python3 -m json.tool
    echo
fi

echo "6️⃣ 提交幂运算任务 (3^4):"
curl -s -X POST "$API_URL/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "a": 3,
    "b": 4,
    "operation_chain": "power_sqrt"
  }' | python3 -m json.tool
echo

echo "7️⃣ 获取任务列表:"
sleep 2
curl -s -X GET "$API_URL/tasks?limit=5" | python3 -m json.tool
echo

echo "8️⃣ 测试错误情况 - 无效任务链:"
curl -s -X POST "$API_URL/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "a": 10,
    "b": 5,
    "operation_chain": "invalid_chain"
  }' | python3 -m json.tool
echo

echo "9️⃣ 测试错误情况 - 查询不存在的任务:"
curl -s -X GET "$API_URL/status/non-existent-task" | python3 -m json.tool
echo

echo "✅ curl测试完成!"
echo "=" * 50
echo "💡 提示:"
echo "   - 确保FastAPI服务器在 http://localhost:8000 运行"
echo "   - 确保Celery worker正在运行"
echo "   - 确保Redis服务器正在运行"
