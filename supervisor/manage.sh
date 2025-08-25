#!/bin/bash

# Supervisor管理脚本
# 用于启动、停止和管理Task Chain项目的所有服务

PROJECT_DIR="/Users/apple/opt/difyz_08/github_001/002/task_chain"
SUPERVISOR_CONF="$PROJECT_DIR/supervisor/supervisord.conf"
SUPERVISOR_PID="/tmp/supervisord.pid"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${2}${1}${NC}"
}

# 检查supervisor是否安装
check_supervisor() {
    if ! command -v supervisord &> /dev/null; then
        print_message "❌ Supervisor未安装，请先安装: pip install supervisor" $RED
        exit 1
    fi
}

# 启动supervisor
start_supervisor() {
    print_message "🚀 启动Supervisor..." $BLUE
    
    if [ -f "$SUPERVISOR_PID" ]; then
        print_message "⚠️  Supervisor可能已在运行，检查状态..." $YELLOW
        if ps -p $(cat $SUPERVISOR_PID) > /dev/null 2>&1; then
            print_message "✅ Supervisor已在运行" $GREEN
            return 0
        else
            print_message "🔄 清理旧的PID文件..." $YELLOW
            rm -f $SUPERVISOR_PID
        fi
    fi
    
    supervisord -c $SUPERVISOR_CONF
    
    if [ $? -eq 0 ]; then
        print_message "✅ Supervisor启动成功" $GREEN
        sleep 2
        status_services
    else
        print_message "❌ Supervisor启动失败" $RED
        exit 1
    fi
}

# 停止supervisor
stop_supervisor() {
    print_message "🛑 停止Supervisor..." $BLUE
    
    if [ -f "$SUPERVISOR_PID" ]; then
        supervisorctl -c $SUPERVISOR_CONF shutdown
        if [ $? -eq 0 ]; then
            print_message "✅ Supervisor已停止" $GREEN
        else
            print_message "❌ Supervisor停止失败" $RED
        fi
    else
        print_message "⚠️  Supervisor未运行" $YELLOW
    fi
}

# 重启supervisor
restart_supervisor() {
    print_message "🔄 重启Supervisor..." $BLUE
    stop_supervisor
    sleep 2
    start_supervisor
}

# 查看服务状态
status_services() {
    print_message "📊 服务状态:" $BLUE
    supervisorctl -c $SUPERVISOR_CONF status
}

# 启动所有服务
start_all() {
    print_message "🚀 启动所有服务..." $BLUE
    supervisorctl -c $SUPERVISOR_CONF start all
    status_services
}

# 停止所有服务
stop_all() {
    print_message "🛑 停止所有服务..." $BLUE
    supervisorctl -c $SUPERVISOR_CONF stop all
    status_services
}

# 重启所有服务
restart_all() {
    print_message "🔄 重启所有服务..." $BLUE
    supervisorctl -c $SUPERVISOR_CONF restart all
    status_services
}

# 启动特定服务
start_service() {
    if [ -z "$1" ]; then
        print_message "❌ 请指定服务名称: celery-worker, fastapi-server, web-server" $RED
        return 1
    fi
    
    print_message "🚀 启动服务: $1" $BLUE
    supervisorctl -c $SUPERVISOR_CONF start $1
    supervisorctl -c $SUPERVISOR_CONF status $1
}

# 停止特定服务
stop_service() {
    if [ -z "$1" ]; then
        print_message "❌ 请指定服务名称: celery-worker, fastapi-server, web-server" $RED
        return 1
    fi
    
    print_message "🛑 停止服务: $1" $BLUE
    supervisorctl -c $SUPERVISOR_CONF stop $1
    supervisorctl -c $SUPERVISOR_CONF status $1
}

# 重启特定服务
restart_service() {
    if [ -z "$1" ]; then
        print_message "❌ 请指定服务名称: celery-worker, fastapi-server, web-server" $RED
        return 1
    fi
    
    print_message "🔄 重启服务: $1" $BLUE
    supervisorctl -c $SUPERVISOR_CONF restart $1
    supervisorctl -c $SUPERVISOR_CONF status $1
}

# 查看日志
view_logs() {
    service_name=${1:-"celery-worker"}
    log_file="$PROJECT_DIR/logs/${service_name//-/_}.log"
    
    if [ -f "$log_file" ]; then
        print_message "📋 查看日志: $service_name" $BLUE
        tail -f $log_file
    else
        print_message "❌ 日志文件不存在: $log_file" $RED
    fi
}

# 清理日志
clean_logs() {
    print_message "🧹 清理日志文件..." $BLUE
    rm -f $PROJECT_DIR/logs/*.log
    print_message "✅ 日志清理完成" $GREEN
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}Task Chain Supervisor管理脚本${NC}"
    echo ""
    echo "用法: $0 [命令] [参数]"
    echo ""
    echo "Supervisor管理:"
    echo "  start-supervisor    启动Supervisor"
    echo "  stop-supervisor     停止Supervisor"
    echo "  restart-supervisor  重启Supervisor"
    echo ""
    echo "服务管理:"
    echo "  status              查看所有服务状态"
    echo "  start-all           启动所有服务"
    echo "  stop-all            停止所有服务"
    echo "  restart-all         重启所有服务"
    echo ""
    echo "单个服务管理:"
    echo "  start <service>     启动指定服务"
    echo "  stop <service>      停止指定服务"
    echo "  restart <service>   重启指定服务"
    echo ""
    echo "可用服务名称:"
    echo "  - celery-worker     Celery任务处理器"
    echo "  - fastapi-server    FastAPI后端服务"
    echo "  - web-server        Web前端服务"
    echo ""
    echo "日志管理:"
    echo "  logs [service]      查看服务日志 (默认: celery-worker)"
    echo "  clean-logs          清理所有日志文件"
    echo ""
    echo "示例:"
    echo "  $0 start-supervisor           # 启动Supervisor"
    echo "  $0 start-all                  # 启动所有服务"
    echo "  $0 restart celery-worker      # 重启Celery Worker"
    echo "  $0 logs fastapi-server        # 查看FastAPI日志"
    echo "  $0 status                     # 查看服务状态"
}

# 主函数
main() {
    check_supervisor
    
    case "$1" in
        "start-supervisor")
            start_supervisor
            ;;
        "stop-supervisor")
            stop_supervisor
            ;;
        "restart-supervisor")
            restart_supervisor
            ;;
        "status")
            status_services
            ;;
        "start-all")
            start_all
            ;;
        "stop-all")
            stop_all
            ;;
        "restart-all")
            restart_all
            ;;
        "start")
            start_service $2
            ;;
        "stop")
            stop_service $2
            ;;
        "restart")
            restart_service $2
            ;;
        "logs")
            view_logs $2
            ;;
        "clean-logs")
            clean_logs
            ;;
        "help"|"-h"|"--help"|"")
            show_help
            ;;
        *)
            print_message "❌ 未知命令: $1" $RED
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 切换到项目目录
cd $PROJECT_DIR

# 执行主函数
main "$@"
