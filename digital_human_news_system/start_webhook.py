#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键启动脚本 - 启动 Webhook 服务供 n8n 调用
"""

import os
import sys
import subprocess
import webbrowser
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     🤖 AI数字人新闻系统 - n8n Webhook 服务                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖...")
    try:
        import requests
        print("   ✅ requests")
    except ImportError:
        print("   ⚠️  requests 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)

    try:
        import schedule
        print("   ✅ schedule")
    except ImportError:
        print("   ⚠️  schedule 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "schedule"], check=True)

    print("   ✅ 所有依赖就绪\n")

def start_webhook_server():
    """启动 Webhook 服务"""
    print("🚀 启动 Webhook 服务...")
    print("   地址: http://localhost:8080")
    print("   端点:")
    print("   ├── POST /webhook/trigger  触发完整流程")
    print("   ├── POST /webhook/fetch   抓取新闻")
    print("   ├── POST /webhook/create  AI二创")
    print("   ├── POST /webhook/generate 生成视频")
    print("   ├── POST /webhook/publish 发布视频")
    print("   └── GET  /health         健康检查")
    print()
    print("   按 Ctrl+C 停止服务\n")

    # 启动服务
    from n8n_webhook import run_server
    run_server('0.0.0.0', 8080)

def open_n8n():
    """打开 n8n"""
    print("🌐 正在打开 n8n...")
    webbrowser.open("http://localhost:5678")

def main():
    clear_screen()
    print_banner()

    print("=" * 60)
    print("  配置信息")
    print("=" * 60)
    print(f"  收件邮箱: h13751019800@163.com")
    print(f"  Webhook端口: 8080")
    print("=" * 60 + "\n")

    check_dependencies()

    # 询问是否打开 n8n
    print("📌 是否打开 n8n 界面？")
    print("   (y) 是 - 打开浏览器")
    print("   (n) 否 - 仅启动服务")
    print()

    choice = input("请选择 (y/n): ").strip().lower()

    if choice == 'y':
        open_n8n()

    print("\n" + "=" * 60)
    start_webhook_server()

if __name__ == '__main__':
    main()
