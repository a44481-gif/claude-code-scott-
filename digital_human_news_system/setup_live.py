#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一鍵直播配置向導
引導用戶完成直播配置
"""

import os
import sys
import json
import subprocess
import webbrowser
from pathlib import Path


def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║       AI數字人直播 - 一鍵配置向導                          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_step(num, total, title):
    print()
    print("=" * 55)
    print(f"  步驟 {num}/{total}: {title}")
    print("=" * 55)


def check_obs_installed():
    """檢查OBS是否已安裝"""
    obs_paths = [
        r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
        r"C:\Program Files (x86)\obs-studio\bin\32bit\obs32.exe",
    ]

    for path in obs_paths:
        if os.path.exists(path):
            return True, path

    return False, None


def open_douyin_creator():
    """打開抖音創作平台"""
    url = "https://creator.douyin.com/"
    print(f"正在打開: {url}")
    webbrowser.open(url)


def update_live_config(stream_server, stream_key):
    """更新直播配置"""
    config_path = 'config/live_config.json'

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    config['live']['platforms']['douyin']['stream_server'] = stream_server
    config['live']['platforms']['douyin']['stream_key'] = stream_key

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"配置已更新!")


def download_obs():
    """下載OBS"""
    url = "https://obsproject.com/downloads/latest/obs-studio-latest.exe"
    print(f"正在下載OBS: {url}")
    webbrowser.open(url)
    input("\n下載完成後，按回車繼續...")


def main():
    print_banner()

    total_steps = 5

    # ========== 步驟1 ==========
    print_step(1, total_steps, "檢查OBS安裝狀態")

    obs_installed, obs_path = check_obs_installed()

    if obs_installed:
        print(f"  [OK] OBS已安裝: {obs_path}")
    else:
        print("  [X] OBS未安裝")
        print()
        print("  請選擇:")
        print("  1. 自動下載OBS")
        print("  2. 手動下載")
        print("  3. 跳過（稍後手動安裝）")
        choice = input("\n  請選擇 (1/2/3): ").strip()

        if choice == '1':
            download_obs()
        elif choice == '2':
            webbrowser.open("https://obsproject.com/")
            input("\n  下載完成後，按回車繼續...")

    # ========== 步驟2 ==========
    print_step(2, total_steps, "獲取抖音推流地址")

    print("""
  請按照以下步驟獲取推流地址:
  1. 打開抖音創作服務平台
  2. 登錄你的抖音帳號
  3. 點擊「直播間管理」
  4. 點擊「電腦直播」
  5. 複製「推流地址」
    """)

    print("  是否打開抖音創作平台? (y/n)")
    choice = input("  : ").strip().lower()

    if choice == 'y':
        open_douyin_creator()

    print()
    stream_server = input("  請輸入推流服務器地址: ").strip()
    stream_key = input("  請輸入推流密鑰: ").strip()

    if stream_server and stream_key:
        update_live_config(stream_server, stream_key)
    else:
        print("  [跳過] 未填入推流信息，稍後可在 config/live_config.json 中配置")

    # ========== 步驟3 ==========
    print_step(3, total_steps, "生成直播視頻")

    print("  正在生成直播用視頻...")
    try:
        result = subprocess.run(
            [sys.executable, 'generate_live_videos.py', '-c', '5'],
            capture_output=False
        )
        print("  [OK] 視頻生成完成")
    except Exception as e:
        print(f"  [X] 視頻生成失敗: {e}")

    # ========== 步驟4 ==========
    print_step(4, total_steps, "配置OBS場景")

    print("""
  請在OBS中進行以下配置:

  1. 添加場景
     - 點擊「場景」→「+」
     - 名稱: 數字人直播

  2. 添加來源
     - 點擊「來源」→「+」→「媒體源」
     - 選擇 data/output 目錄下的視頻
     - 勾選「循環」

  3. 添加字幕
     - 點擊「來源」→「+」→「文字」
     - 名稱: 字幕
     - 調整字體大小和位置

  4. 配置推流
     - 點擊「設置」→「推流」
     - 服務器: 自定義
     - 粘貼推流地址

  5. 設置快捷鍵
     - 設置 → 快捷鍵
     - 開始推流: Ctrl+Shift+S
     - 停止推流: Ctrl+Shift+D
    """)

    print("  是否打開OBS? (y/n)")
    choice = input("  : ").strip().lower()

    if choice == 'y' and obs_path:
        subprocess.Popen(f'"{obs_path}"')
    else:
        input("\n  按回車打開配置指南...")

    # ========== 步驟5 ==========
    print_step(5, total_steps, "啟動直播系統")

    print("""
  配置完成！選擇啟動方式:

  1. 啟動Webhook服務 (供n8n調用)
     python n8n_webhook.py

  2. 啟動直播助手 (獨立運行)
     python live_assistant.py

  3. 在n8n中導入直播工作流
     n8n_live_workflow.json
    """)

    print("=" * 55)
    print("  配置完成！")
    print("=" * 55)
    print()
    print("  文件位置: d:\\claude mini max 2.7\\digital_human_news_system")
    print()
    print("  下一步:")
    print("  1. 啟動 n8n_webhook.py")
    print("  2. 在n8n中導入 n8n_live_workflow.json")
    print("  3. 點擊OBS「開始推流」")
    print()


if __name__ == '__main__':
    main()
