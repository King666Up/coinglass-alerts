#!/bin/bash

# CoinGlass 项目启动脚本

echo "🚀 启动 CoinGlass 加密货币告警系统..."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行安装命令"
    echo "   cd /home/king/.openclaw/workspace/coinglass-alerts"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo "   pip install pycryptodome"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

echo "✅ 虚拟环境已激活"

# 检查是否传入了参数
if [ $# -eq 0 ]; then
    echo "📖 用法:"
    echo "   ./run_project.sh                    # 显示帮助信息"
    echo "   ./run_project.sh start             # 启动连续监控模式"
    echo "   ./run_project.sh single            # 运行单次检查"
    echo "   ./run_project.sh test              # 运行测试"
    echo "   ./run_project.sh example           # 运行示例"
    echo "   ./run_project.sh shell             # 进入虚拟环境shell"
    exit 0
fi

case $1 in
    "start")
        echo "🎬 启动连续监控模式..."
        python src/main.py
        ;;
    "single")
        echo "🔍 运行单次监控检查..."
        python src/main.py --single
        ;;
    "test")
        echo "🧪 运行项目测试..."
        python test_project.py
        ;;
    "example")
        echo "📚 运行示例代码..."
        python examples/basic_usage.py
        ;;
    "shell")
        echo "🐚 进入虚拟环境shell..."
        echo "   输入 'exit' 退出虚拟环境shell"
        bash --rcfile <(echo '. venv/bin/activate')
        ;;
    *)
        echo "❌ 未知命令: $1"
        echo "📖 有效命令: start, single, test, example, shell"
        ;;
esac

# 退出虚拟环境
deactivate
echo "✅ 虚拟环境已退出"