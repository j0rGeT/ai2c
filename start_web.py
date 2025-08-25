#!/usr/bin/env python3
"""
AI内容创作系统 - Web应用启动器
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """检查必要的依赖是否已安装"""
    try:
        import streamlit
        import openai
        import anthropic
        return True
    except ImportError as e:
        print(f"❌ 缺少必要依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_env_file():
    """检查环境变量文件是否存在"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️ 未找到 .env 文件")
            print("请复制 .env.example 为 .env 并配置您的API密钥:")
            print("cp .env.example .env")
            return False
        else:
            print("⚠️ 未找到环境配置文件")
            return False
    
    return True

def create_directories():
    """创建必要的目录"""
    directories = [
        "outputs/videos",
        "outputs/audio", 
        "outputs/articles",
        "temp",
        ".streamlit"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def main():
    """主函数"""
    print("🚀 启动AI内容创作系统Web界面...")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查环境配置
    if not check_env_file():
        print("💡 您可以在没有API密钥的情况下预览界面，但功能将受限")
        response = input("是否继续启动? (y/N): ").lower()
        if response != 'y':
            sys.exit(1)
    
    # 创建目录
    create_directories()
    
    # 启动Streamlit应用
    print("🌐 正在启动Web服务器...")
    print("📱 应用将在浏览器中自动打开: http://localhost:8501")
    print("⏹️ 按 Ctrl+C 停止服务")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "web_app.py",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--server.fileWatcherType", "none"
        ])
    except KeyboardInterrupt:
        print("\n👋 Web服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()