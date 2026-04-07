# -*- coding: utf-8 -*-
"""
CoBM 雲端 Agent - 本地觸發器
向雲端發起任務並接收結果
"""

import os
import sys
import json
import time
import requests
import hashlib
from datetime import datetime
from pathlib import Path

# 配置
CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY", "cobm-secret-key-2026")

class CloudAgent:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = (api_url or CLOUD_API_URL).rstrip("/")
        self.api_key = api_key or API_KEY
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": self.api_key})

    def _request(self, method: str, endpoint: str, **kwargs):
        """發送 API 請求"""
        url = f"{self.api_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """健康檢查"""
        return self._request("GET", "/health")

    def create_task(self, task_type: str, params: dict = None, email_to: str = None, callback_url: str = None) -> dict:
        """創建任務"""
        return self._request("POST", "/api/v1/tasks", json={
            "task_type": task_type,
            "params": params or {},
            "email_to": email_to or "scott365888@gmail.com",
            "callback_url": callback_url
        })

    def get_task(self, task_id: str) -> dict:
        """查詢任務狀態"""
        return self._request("GET", f"/api/v1/tasks/{task_id}")

    def wait_for_completion(self, task_id: str, poll_interval: int = 3, timeout: int = 300) -> dict:
        """等待任務完成"""
        start = time.time()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 監控任務 {task_id}...")

        while time.time() - start < timeout:
            result = self.get_task(task_id)
            status = result.get("status")

            if status == "completed":
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 任務完成！")
                return result

            if status == "failed":
                raise Exception(f"任務失敗: {result.get('error')}")

            print(f"[{datetime.now().strftime('%H:%M:%S')}] 狀態: {status}...", end="\r")
            time.sleep(poll_interval)

        raise TimeoutError(f"任務執行超時 ({timeout}秒)")

    def download_report(self, task_id: str, save_dir: str = None) -> str:
        """下載報告"""
        save_dir = Path(save_dir or "./cloud_results")
        save_dir.mkdir(exist_ok=True)

        response = self.session.get(f"{self.api_url}/api/v1/tasks/{task_id}/download", stream=True)
        response.raise_for_status()

        filename = response.headers.get("Content-Disposition", "").split("filename=")[-1].strip('"')
        if not filename:
            filename = f"report_{task_id}.pptx"

        filepath = save_dir / filename
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"報告已下載: {filepath}")
        return str(filepath)

    def run_full_pipeline(self, params: dict = None, email_to: str = None, wait: bool = True) -> dict:
        """執行全流程"""
        print("=" * 60)
        print("CoBM 雲端全流程自動化")
        print("=" * 60)

        # 創建任務
        print(f"向雲端提交任務...")
        result = self.create_task(
            task_type="full_pipeline",
            params=params or {},
            email_to=email_to or "scott365888@gmail.com"
        )

        task_id = result["task_id"]
        print(f"任務已創建: {task_id}")

        if not wait:
            return {"task_id": task_id, "status": "pending"}

        # 等待完成
        print("等待雲端處理中...")
        task_result = self.wait_for_completion(task_id)

        # 下載報告
        print("下載報告...")
        report_path = self.download_report(task_id)

        return {
            "task_id": task_id,
            "result": task_result.get("result"),
            "report_path": report_path
        }

    def run_report(self, title: str, content: dict = None) -> dict:
        """僅生成報告"""
        return self.create_task(
            task_type="report",
            params={"title": title, "content": content or {}}
        )

    def run_crawl(self, params: dict = None) -> dict:
        """僅爬取數據"""
        return self.create_task(
            task_type="crawl",
            params=params or {}
        )

# ============== CLI 界面 ==============

def main():
    import argparse

    parser = argparse.ArgumentParser(description="CoBM 雲端 Agent 本地觸發器")
    parser.add_argument("--url", default=CLOUD_API_URL, help="雲端 API 地址")
    parser.add_argument("--key", default=API_KEY, help="API Key")
    parser.add_argument("--type", "-t", default="full_pipeline",
                        choices=["full_pipeline", "report", "crawl", "analyze"],
                        help="任務類型")
    parser.add_argument("--email", "-e", default="scott365888@gmail.com", help="結果發送郵箱")
    parser.add_argument("--no-wait", action="store_true", help="不等結果返回")
    parser.add_argument("--save-dir", "-o", default="./cloud_results", help="報告保存目錄")

    args = parser.parse_args()

    agent = CloudAgent(api_url=args.url, api_key=args.key)

    # 健康檢查
    try:
        health = agent.health_check()
        print(f"雲端服務: ✅ {health.get('time')}")
    except Exception as e:
        print(f"雲端服務: ❌ 連接失敗 - {e}")
        print(f"請確保雲端服務已啟動: {args.url}")
        sys.exit(1)

    # 執行任務
    try:
        if args.type == "full_pipeline":
            result = agent.run_full_pipeline(email_to=args.email, wait=not args.no_wait)
        elif args.type == "report":
            result = agent.create_task(task_type="report", params={"title": "CoBM 報告"})
        elif args.type == "crawl":
            result = agent.create_task(task_type="crawl", params={})
        else:
            result = agent.create_task(task_type="analyze", params={})

        print("\n結果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"\n錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
