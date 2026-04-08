"""
Cloud Agent HTTP 服務器
=======================
功能：
  - WebHook 端點：接收外部觸發
  - Cron 端點：定時觸發每日報告
  - 健康檢查：/health
  - 任務狀態：/api/task/{id}

Example:
  # 啟動服務器
  python -m cloud_agent.http_server

  # WebHook 觸發
  curl -X POST http://localhost:8080/webhook/task \
    -H "Content-Type: application/json" \
    -d '{"task":"分析今日市場","trigger":"webhook"}'

  # Cron 觸發
  curl http://localhost:8080/cron/daily
"""

import os, sys, json, logging, threading, traceback
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.parse

# 確保 cloud_agent 在路徑中
_AGENT_DIR = Path(__file__).parent.resolve()
_ROOT_DIR  = _AGENT_DIR.parent.resolve()
sys.path.insert(0, str(_ROOT_DIR))

# 延遲導入，避免循環
_http_server_instance = None
_engine = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
log = logging.getLogger("HTTPServer")

# ═══════════════════════════════════════════════════════════════════════════
# 全域引擎單例
# ═══════════════════════════════════════════════════════════════════════════

def get_engine():
    global _engine
    if _engine is None:
        from cloud_agent.orchestrator import CloudAgentEngine, load_config
        _engine = CloudAgentEngine(load_config())
    return _engine

# ═══════════════════════════════════════════════════════════════════════════
# 請求處理器
# ═══════════════════════════════════════════════════════════════════════════

class CloudAgentHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        log.info(f"[HTTP] {args[0]}")

    def send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path
        qs     = parse_qs(parsed.query)

        # 健康檢查
        if path == "/health":
            self.send_json(200, {"status": "ok", "time": datetime.now().isoformat()})
            return

        # Cron 每日觸發
        if path == "/cron/daily":
            self._handle_cron_daily()
            return

        # 任務列表
        if path == "/api/tasks":
            self._handle_list_tasks(qs)
            return

        # 任務狀態
        if path.startswith("/api/task/"):
            task_id = path.split("/")[-1]
            self._handle_get_task(task_id)
            return

        self.send_json(404, {"error": "Not Found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path   = parsed.path
        length  = int(self.headers.get("Content-Length", 0))
        body    = self.rfile.read(length).decode("utf-8", errors="replace")

        if path == "/webhook/task":
            self._handle_webhook_task(body)
            return

        if path == "/api/submit":
            self._handle_api_submit(body)
            return

        self.send_json(404, {"error": "Not Found"})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    # ─── 處理方法 ───────────────────────────────────────────────────────────

    def _handle_webhook_task(self, body: str):
        try:
            data = json.loads(body)
            task_desc = data.get("task", "")
            secret    = data.get("secret", "")

            # 驗證密鑰（如果配置了）
            cfg = get_engine().cfg
            webhook_secret = cfg.get("webhook", {}).get("secret", "")
            if webhook_secret and secret != webhook_secret:
                self.send_json(401, {"error": "Unauthorized"})
                return

            if not task_desc:
                self.send_json(400, {"error": "task 字段不能為空"})

            # 異步執行
            thread = threading.Thread(
                target=lambda: get_engine().run_task(task_desc, trigger="webhook"),
                daemon=True
            )
            thread.start()

            self.send_json(202, {
                "message": "任務已接收並異步執行",
                "task_desc": task_desc[:100],
            })

        except json.JSONDecodeError:
            self.send_json(400, {"error": "無效的 JSON"})
        except Exception as e:
            log.error(f"[Webhook] 錯誤: {e}")
            traceback.print_exc()
            self.send_json(500, {"error": str(e)})

    def _handle_api_submit(self, body: str):
        try:
            data = json.loads(body)
            prompts = data.get("tasks", [])
            if isinstance(data.get("task"), str):
                prompts = [data["task"]]

            if not prompts:
                self.send_json(400, {"error": "tasks 列表不能為空"})

            engine = get_engine()
            results = []

            def _run(prompt):
                t = engine.run_task(prompt, trigger="api")
                results.append({"id": t.id, "status": t.status_enum.value})

            threads = [threading.Thread(target=_run, args=(p,)) for p in prompts]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            self.send_json(200, {"tasks": results})

        except Exception as e:
            log.error(f"[API] 錯誤: {e}")
            self.send_json(500, {"error": str(e)})

    def _handle_cron_daily(self):
        """每日 Cron 觸發 — 執行每日報告任務"""
        try:
            engine = get_engine()
            cfg = engine.cfg

            # 讀取每日報告模板
            template = cfg.get("agent_templates", {}).get("daily_report", "")
            template = template.replace("{date}", datetime.now().strftime("%Y年%m月%d日"))

            thread = threading.Thread(
                target=lambda: engine.run_task(template, trigger="cron"),
                daemon=True
            )
            thread.start()

            self.send_json(202, {
                "message": "每日報告任務已觸發",
                "time": datetime.now().isoformat(),
            })
            log.info("[Cron] 每日報告已觸發")

        except Exception as e:
            log.error(f"[Cron] 錯誤: {e}")
            self.send_json(500, {"error": str(e)})

    def _handle_list_tasks(self, qs):
        limit = int(qs.get("limit", ["20"])[0])
        engine = get_engine()
        tasks = engine.store.list_tasks(limit=limit)
        self.send_json(200, {
            "tasks": [
                {
                    "id": t.id,
                    "status": t.status_enum.value,
                    "prompt": t.prompt[:80],
                    "trigger": t.trigger,
                    "duration_s": t.duration_s,
                    "created_at": t.created_at,
                }
                for t in tasks
            ]
        })

    def _handle_get_task(self, task_id: str):
        engine = get_engine()
        task = engine.store.get_task(task_id)
        if not task:
            self.send_json(404, {"error": "任務不存在"})
            return

        result = engine.store.get_result(task_id)
        self.send_json(200, {
            "id": task.id,
            "status": task.status_enum.value,
            "prompt": task.prompt,
            "trigger": task.trigger,
            "duration_s": task.duration_s,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "finished_at": task.finished_at,
            "result_preview": (result[:500] if result else None),
            "result_length": len(result) if result else 0,
        })

# ═══════════════════════════════════════════════════════════════════════════
# 服務器啟動
# ═══════════════════════════════════════════════════════════════════════════

def start_server(host: str = "0.0.0.0", port: int = 8080):
    global _http_server_instance
    addr = (host, port)
    _http_server_instance = HTTPServer(addr, CloudAgentHandler)
    log.info(f"Cloud Agent HTTP Server 啟動: http://{host}:{port}")
    log.info("  WebHook 觸發：POST /webhook/task")
    log.info("  Cron 觸發：GET  /cron/daily")
    log.info("  任務列表：GET  /api/tasks")
    log.info("  健康檢查：GET  /health")
    _http_server_instance.serve_forever()

def stop_server():
    global _http_server_instance
    if _http_server_instance:
        _http_server_instance.shutdown()
        log.info("HTTP Server 已停止")

# ═══════════════════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", "-p", type=int, default=8080)
    args = parser.parse_args()
    start_server(args.host, args.port)
