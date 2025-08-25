#!/bin/bash
# Supervisor管理脚本 - Celery Worker管理

PROJECT_DIR="/Users/apple/opt/difyz_08/github_001/002/task_chain"
SUPERVISOR_CONF="$PROJECT_DIR/supervisor/celery_worker.conf"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 检查supervisor是否安装
check_supervisor() {
    if ! command -v supervisord &> /dev/null; then
        print_message $RED "❌ Supervisor未安装，请先安装："
        echo "   macOS: brew install supervisor"
        echo "   Ubuntu: sudo apt-get install supervisor"
        echo "   CentOS: sudo yum install supervisor"
        exit 1
    fi
}

# 启动supervisor守护进程
start_supervisord() {
    print_message $BLUE "🚀 启动Supervisor守护进程..."
    
    # 检查是否已经运行
    if pgrep -f supervisord > /dev/null; then
        print_message $YELLOW "⚠️  Supervisor守护进程已在运行"
        return 0
    fi
    
    # 启动supervisord
    supervisord -c $SUPERVISOR_CONF
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "✅ Supervisor守护进程启动成功"
    else
        print_message $RED "❌ Supervisor守护进程启动失败"
        exit 1
    fi
}

# 停止supervisor守护进程
stop_supervisord() {
    print_message $BLUE "🛑 停止Supervisor守护进程..."
    
    if pgrep -f supervisord > /dev/null; then
        supervisorctl -c $SUPERVISOR_CONF shutdown
        print_message $GREEN "✅ Supervisor守护进程已停止"
    else
        print_message $YELLOW "⚠️  Supervisor守护进程未运行"
    fi
}

# 重启supervisor守护进程
restart_supervisord() {
    print_message $BLUE "🔄 重启Supervisor守护进程..."
    stop_supervisord
    sleep 2
    start_supervisord
}

# 启动Celery worker
start_worker() {
    print_message $BLUE "🚀 启动Celery Worker..."
    supervisorctl -c $SUPERVISOR_CONF start celery_worker
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "✅ Celery Worker启动成功"
    else
        print_message $RED "❌ Celery Worker启动失败"
    fi
}

# 停止Celery worker
stop_worker() {
    print_message $BLUE "🛑 停止Celery Worker..."
    supervisorctl -c $SUPERVISOR_CONF stop celery_worker
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "✅ Celery Worker已停止"
    else
        print_message $RED "❌ Celery Worker停止失败"
    fi
}

# 重启Celery worker
restart_worker() {
    print_message $BLUE "🔄 重启Celery Worker..."
    supervisorctl -c $SUPERVISOR_CONF restart celery_worker
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "✅ Celery Worker重启成功"
    else
        print_message $RED "❌ Celery Worker重启失败"
    fi
}

# 查看状态
status() {
    print_message $BLUE "📊 查看服务状态..."
    supervisorctl -c $SUPERVISOR_CONF status
}

# 查看日志
logs() {
    local service=${1:-celery_worker}
    print_message $BLUE "📋 查看${service}日志..."
    
    case $service in
        "worker"|"celery_worker")
            tail -f $PROJECT_DIR/logs/celery_worker.log
            ;;
        "beat"|"celery_beat")
            tail -f $PROJECT_DIR/logs/celery_beat.log
            ;;
        "error")
            tail -f $PROJECT_DIR/logs/celery_worker_error.log
            ;;
        *)
            echo "可用的日志选项: worker, beat, error"
            ;;
    esac
}

# 显示帮助
show_help() {
    echo "Supervisor Celery Worker 管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start-daemon     启动Supervisor守护进程"
    echo "  stop-daemon      停止Supervisor守护进程"
    echo "  restart-daemon   重启Supervisor守护进程"
    echo "  start            启动Celery Worker"
    echo "  stop             停止Celery Worker"
    echo "  restart          重启Celery Worker"
    echo "  status           查看服务状态"
    echo "  logs [service]   查看日志 (worker|beat|error)"
    echo "  help             显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start-daemon  # 启动supervisor守护进程"
    echo "  $0 start         # 启动worker"
    echo "  $0 logs worker   # 查看worker日志"
}

# 主函数
main() {
    check_supervisor
    
    case "${1:-help}" in
        "start-daemon")
            start_supervisord
            ;;
        "stop-daemon")
            stop_supervisord
            ;;
        "restart-daemon")
            restart_supervisord
            ;;
        "start")
            start_worker
            ;;
        "stop")
            stop_worker
            ;;
        "restart")
            restart_worker
            ;;
        "status")
            status
            ;;
        "logs")
            logs $2
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"
