#!/bin/bash

# AI内容创作系统启动脚本

echo "🚀 启动AI内容创作系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查基础依赖..."
if ! python3 -c "import streamlit, openai, anthropic" &> /dev/null; then
    echo "⚠️ 正在安装基础依赖..."
    pip install -r requirements.txt
fi

# 检查环境文件
if [ ! -f ".env" ]; then
    echo "⚠️ 未找到.env文件"
    if [ -f ".env.example" ]; then
        echo "📝 请复制.env.example为.env并配置API密钥:"
        echo "cp .env.example .env"
        echo "然后编辑.env文件添加您的API密钥"
    fi
fi

# 创建输出目录
mkdir -p outputs/{videos,audio,articles}
mkdir -p temp

# 启动Web界面
echo "🌐 启动Web界面..."
python3 start_web.py