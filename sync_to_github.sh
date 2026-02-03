#!/bin/bash

# CoinGlass告警系统项目同步脚本

set -e  # 遇到错误时退出

echo "🔄 开始同步 CoinGlass 告警系统到 GitHub..."

# 检查是否在项目目录中
if [ ! -f "config.json" ]; then
    echo "❌ 错误: 不在 coinglass-alerts 项目目录中"
    exit 1
fi

echo "✅ 在正确的项目目录中"

# 检查 Git 是否已安装
if ! command -v git &> /dev/null; then
    echo "❌ 错误: Git 未安装"
    exit 1
fi

echo "✅ Git 已安装"

# 检查是否为 Git 仓库
if [ ! -d ".git" ]; then
    echo "❌ 错误: 不是 Git 仓库，正在初始化..."
    git init
    git remote add origin https://github.com/King666Up/coinglass-alerts.git
    echo "✅ Git 仓库已初始化"
else
    echo "✅ Git 仓库已存在"
fi

# 添加所有更改的文件
echo "📦 添加所有更改的文件..."
git add .

# 检查是否有更改
if git diff --cached --quiet; then
    echo "ℹ️  没有更改需要提交"
    echo "✅ 同步完成"
    exit 0
fi

# 获取当前日期和时间
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# 创建提交信息
COMMIT_MSG="🔄 项目更新 ${CURRENT_TIME}
  
  - 🔧 增强基差分析功能
  - 🤖 集成LLM智能分析
  - 📊 添加反转信号检测
  - 📈 优化策略生成算法
  - 📝 更新文档和配置
  - 🚀 性能优化"

echo "📝 提交信息: $COMMIT_MSG"

# 提交更改
git commit -m "$COMMIT_MSG"

# 获取当前分支
BRANCH=$(git branch --show-current)

if [ -z "$BRANCH" ]; then
    BRANCH="main"
    echo "ℹ️  未检测到当前分支，使用默认分支: $BRANCH"
fi

# 推送到远程仓库
echo "📤 推送到 GitHub 分支: $BRANCH"

# 尝试推送
if git push origin "$BRANCH"; then
    echo "✅ 成功推送到 GitHub"
    echo "🎉 CoinGlass 告警系统项目已成功同步到 GitHub!"
    echo "🔗 仓库地址: https://github.com/King666Up/coinglass-alerts"
else
    echo "⚠️  推送失败，尝试拉取远程更改并合并..."
    
    # 拉取远程更改并合并
    git pull origin "$BRANCH" --rebase=false
    
    # 再次尝试推送
    if git push origin "$BRANCH"; then
        echo "✅ 成功推送到 GitHub (经过合并)"
        echo "🎉 CoinGlass 告警系统项目已成功同步到 GitHub!"
    else
        echo "❌ 无法推送更改到 GitHub"
        echo "💡 请检查您的网络连接和 GitHub 凭据"
        exit 1
    fi
fi

echo ""
echo "📋 项目状态:"
git status

echo ""
echo "✅ 同步完成！项目已成功更新到 GitHub。"