#!/bin/bash
#
# 系统监控采集脚本 - 启动管理脚本
# 用于管理Python监控采集进程
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/monitor_collector.py"
VENV_DIR="${SCRIPT_DIR}/venv"
LOG_FILE="${SCRIPT_DIR}/monitor.log"
PID_FILE="${SCRIPT_DIR}/monitor.pid"
REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.txt"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        return 0
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        return 0
    else
        log_error "未找到Python解释器，请安装Python 3"
        exit 1
    fi
}

create_venv() {
    if [ ! -d "${VENV_DIR}" ]; then
        log_info "创建虚拟环境..."
        ${PYTHON_CMD} -m venv ${VENV_DIR}
        log_info "虚拟环境创建成功"
    else
        log_info "虚拟环境已存在"
    fi
}

install_requirements() {
    log_info "安装Python依赖..."
    source ${VENV_DIR}/bin/activate
    pip install --upgrade pip
    if [ -f "${REQUIREMENTS_FILE}" ]; then
        pip install -r ${REQUIREMENTS_FILE}
    else
        pip install psutil mysql-connector-python
    fi
    deactivate
    log_info "依赖安装完成"
}

check_dependencies() {
    log_info "检查依赖..."
    check_python
    create_venv
    install_requirements
}

start_monitor() {
    if [ -f "${PID_FILE}" ]; then
        OLD_PID=$(cat ${PID_FILE})
        if kill -0 ${OLD_PID} 2>/dev/null; then
            log_error "监控脚本已在运行中 (PID: ${OLD_PID})"
            exit 1
        else
            log_warn "清理旧的PID文件"
            rm -f ${PID_FILE}
        fi
    fi

    log_info "启动系统监控采集脚本..."
    source ${VENV_DIR}/bin/activate

    nohup python3 ${PYTHON_SCRIPT} >> ${LOG_FILE} 2>&1 &
    NEW_PID=$!

    deactivate

    echo ${NEW_PID} > ${PID_FILE}
    sleep 1

    if kill -0 ${NEW_PID} 2>/dev/null; then
        log_info "监控脚本已启动成功 (PID: ${NEW_PID})"
        log_info "日志文件: ${LOG_FILE}"
    else
        log_error "启动失败，请检查日志"
        exit 1
    fi
}

stop_monitor() {
    if [ ! -f "${PID_FILE}" ]; then
        log_warn "PID文件不存在，监控脚本可能未在运行"
        return 0
    fi

    PID=$(cat ${PID_FILE})

    if [ -z "${PID}" ]; then
        log_warn "PID文件为空"
        rm -f ${PID_FILE}
        return 0
    fi

    if kill -0 ${PID} 2>/dev/null; then
        log_info "停止监控脚本 (PID: ${PID})..."
        kill ${PID}
        rm -f ${PID_FILE}
        log_info "监控脚本已停止"
    else
        log_warn "进程不存在，清理PID文件"
        rm -f ${PID_FILE}
    fi
}

restart_monitor() {
    log_info "重启监控脚本..."
    stop_monitor
    sleep 2
    start_monitor
}

status_monitor() {
    if [ -f "${PID_FILE}" ]; then
        PID=$(cat ${PID_FILE})
        if kill -0 ${PID} 2>/dev/null; then
            log_info "监控脚本正在运行 (PID: ${PID})"
            return 0
        else
            log_warn "进程已停止，但PID文件存在"
            return 1
        fi
    else
        log_warn "监控脚本未运行"
        return 1
    fi
}

logs_monitor() {
    if [ -f "${LOG_FILE}" ]; then
        tail -f ${LOG_FILE}
    else
        log_error "日志文件不存在"
        exit 1
    fi
}

show_help() {
    echo "用法: $0 {start|stop|restart|status|logs|install}"
    echo ""
    echo "命令说明:"
    echo "  start    - 启动监控采集脚本"
    echo "  stop     - 停止监控采集脚本"
    echo "  restart  - 重启监控采集脚本"
    echo "  status   - 查看监控脚本运行状态"
    echo "  logs     - 实时查看监控日志"
    echo "  install  - 安装依赖并初始化环境"
    echo ""
}

case "$1" in
    start)
        check_dependencies
        start_monitor
        ;;
    stop)
        stop_monitor
        ;;
    restart)
        stop_monitor
        sleep 2
        check_dependencies
        start_monitor
        ;;
    status)
        status_monitor
        ;;
    logs)
        logs_monitor
        ;;
    install)
        check_dependencies
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "未知命令: $1"
        show_help
        exit 1
        ;;
esac
