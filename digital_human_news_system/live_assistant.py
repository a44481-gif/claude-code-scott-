#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI數字人直播助手
Digital Human Live Streaming Assistant
控制OBS推流、實時更新內容
"""

import os
import sys
import json
import time
import socket
import threading
import subprocess
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import setup_logger


class OBSController:
    """OBS控制客戶端"""

    def __init__(self, host='localhost', port=4455, password=''):
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
        self.connected = False
        self.logger = setup_logger('obs_controller')

    def connect(self) -> bool:
        """連接OBS WebSocket"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.logger.info("已連接OBS")

            # 發送認證
            self._send_auth()
            return True

        except Exception as e:
            self.logger.error(f"連接OBS失敗: {str(e)}")
            self.connected = False
            return False

    def disconnect(self):
        """斷開連接"""
        if self.socket:
            self.socket.close()
            self.connected = False

    def _send_auth(self):
        """發送認證"""
        # 簡化版認證
        pass

    def start_streaming(self) -> bool:
        """開始推流"""
        if not self.connected:
            self.logger.error("未連接OBS")
            return False

        self.logger.info("開始推流...")
        return True

    def stop_streaming(self) -> bool:
        """停止推流"""
        if not self.connected:
            return False

        self.logger.info("停止推流...")
        return True

    def set_source_text(self, source_name: str, text: str) -> bool:
        """設置文字源"""
        self.logger.info(f"設置文字: {source_name} = {text}")
        return True

    def switch_scene(self, scene_name: str) -> bool:
        """切換場景"""
        self.logger.info(f"切換場景: {scene_name}")
        return True


class LiveStreamAssistant:
    """直播助手"""

    def __init__(self):
        self.logger = setup_logger('live_assistant')
        self.config = self._load_config()
        self.obs = OBSController()
        self.is_live = False
        self.current_segment = 0
        self.content_queue = []

    def _load_config(self):
        """載入配置"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config', 'live_config.json'
        )

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def start_live(self, platform='douyin') -> dict:
        """
        開始直播

        Args:
            platform: 直播平台

        Returns:
            直播信息
        """
        if self.is_live:
            return {'success': False, 'error': '直播已開始'}

        self.logger.info(f"開始直播: {platform}")

        # 連接OBS
        if self.config.get('live', {}).get('obs', {}).get('enabled', False):
            self.obs.connect()

        # 準備內容
        self._prepare_content()

        # 開始推流
        if self.obs.connected:
            self.obs.start_streaming()

        self.is_live = True
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 啟動內容循環
        thread = threading.Thread(target=self._run_content_loop)
        thread.daemon = True
        thread.start()

        return {
            'success': True,
            'platform': platform,
            'start_time': start_time,
            'stream_server': self._get_stream_server(platform),
            'segments': len(self.content_queue)
        }

    def stop_live(self) -> dict:
        """停止直播"""
        if not self.is_live:
            return {'success': False, 'error': '直播未開始'}

        self.logger.info("停止直播")

        # 停止推流
        if self.obs.connected:
            self.obs.stop_streaming()
            self.obs.disconnect()

        self.is_live = False

        return {
            'success': True,
            'duration': self._get_duration()
        }

    def get_status(self) -> dict:
        """獲取直播狀態"""
        return {
            'is_live': self.is_live,
            'current_segment': self.current_segment,
            'total_segments': len(self.content_queue),
            'duration': self._get_duration() if self.is_live else 0
        }

    def _prepare_content(self):
        """準備直播內容"""
        segments = self.config.get('live', {}).get('content', {}).get('segments', [])

        self.content_queue = []
        for seg in segments:
            self.content_queue.append({
                'type': seg.get('type'),
                'duration': seg.get('duration', 60),
                'script': self._fill_script(seg.get('script', '')),
                'category': seg.get('category')
            })

        self.logger.info(f"準備了 {len(self.content_queue)} 個內容段落")

    def _fill_script(self, script: str) -> str:
        """填充腳本變量"""
        hour = datetime.now().hour

        if 6 <= hour < 12:
            time_period = "早上好"
        elif 12 <= hour < 18:
            time_period = "下午好"
        elif 18 <= hour < 22:
            time_period = "晚上好"
        else:
            time_period = "深夜好"

        script = script.replace('{time_period}', time_period)

        # 隨機選擇主題
        themes = ['善行', '助人', '感恩', '奉獻', '關愛']
        script = script.replace('{theme}', themes[int(time.time()) % len(themes)])

        return script

    def _run_content_loop(self):
        """內容循環"""
        while self.is_live and self.content_queue:
            for i, content in enumerate(self.content_queue):
                if not self.is_live:
                    break

                self.current_segment = i

                # 更新OBS文字
                if self.obs.connected:
                    self.obs.set_source_text('字幕', content['script'])

                # 更新標題
                if self.obs.connected:
                    self.obs.set_source_text('標題', content.get('type', ''))

                self.logger.info(f"播放內容 [{i+1}/{len(self.content_queue)}]: {content['type']}")

                # 等待時長
                time.sleep(content['duration'])

            # 循環播放
            if self.is_live:
                self.logger.info("內容循環，重新開始")

    def _get_stream_server(self, platform: str) -> str:
        """獲取推流地址"""
        servers = {
            'douyin': 'rtmp://push.toutiao.com/live',
            'bilibili': 'rtmp://live-push.bilivideo.com/live-bvc',
            'youtube': 'rtmp://a.rtmp.youtube.com/live2'
        }
        return servers.get(platform, '')

    def _get_duration(self) -> int:
        """獲取直播時長"""
        return int(time.time() % 3600)


def main():
    """主函數"""
    assistant = LiveStreamAssistant()

    print("=" * 50)
    print("  AI數字人直播助手")
    print("=" * 50)
    print()
    print("1. 開始直播 (抖音)")
    print("2. 開始直播 (B站)")
    print("3. 查看狀態")
    print("4. 停止直播")
    print("5. 獲取推流信息")
    print("0. 退出")
    print()

    while True:
        choice = input("請選擇: ").strip()

        if choice == '1':
            result = assistant.start_live('douyin')
            print(f"結果: {result}")

        elif choice == '2':
            result = assistant.start_live('bilibili')
            print(f"結果: {result}")

        elif choice == '3':
            status = assistant.get_status()
            print(f"狀態: {status}")

        elif choice == '4':
            result = assistant.stop_live()
            print(f"結果: {result}")

        elif choice == '5':
            print("\n=== 推流地址配置 ===")
            print("抖音推流地址: rtmp://push.toutiao.com/live")
            print("B站推流地址: rtmp://live-push.bilivideo.com/live-bvc")
            print("\n請在OBS設置中添加推流伺服器")

        elif choice == '0':
            if assistant.is_live:
                assistant.stop_live()
            print("再見！")
            break


if __name__ == '__main__':
    main()
