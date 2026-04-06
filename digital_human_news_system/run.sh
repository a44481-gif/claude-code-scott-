#!/bin/bash
# AI数字人新闻系统启动脚本 (Linux/macOS)
# Digital Human News System Startup Script

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 创建必要的目录
mkdir -p data/raw data/processed data/output logs

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "错误: 未找到Python环境"
        echo "请先安装Python 3.8或更高版本"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# 安装依赖 (如果需要)
if [ ! -d "venv" ]; then
    echo "首次运行，创建虚拟环境..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 显示帮助信息
show_help() {
    echo "AI数字人新闻系统"
    echo ""
    echo "用法: ./run.sh [选项]"
    echo ""
    echo "选项:"
    echo "  full        运行完整流程 (默认)"
    echo "  fetch       仅抓取新闻"
    echo "  filter      仅内容筛选"
    echo "  create      仅AI二创"
    echo "  generate    仅视频生成"
    echo "  publish     仅平台发布"
    echo "  scheduler   运行定时任务"
    echo "  test        测试模式"
    echo "  help        显示帮助信息"
    echo ""
}

# 根据参数运行
case "${1:-full}" in
    full)
        echo "开始运行完整流程..."
        $PYTHON_CMD main.py --mode full
        ;;
    fetch|filter|create|generate|publish)
        echo "运行 ${1} 模块..."
        $PYTHON_CMD main.py --mode "$1"
        ;;
    scheduler)
        echo "启动定时任务调度器..."
        $PYTHON_CMD main.py --mode scheduler
        ;;
    test)
        echo "测试模式运行..."
        $PYTHON_CMD main.py --mode full --test
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "未知选项: $1"
        show_help
        exit 1
        ;;
esac
