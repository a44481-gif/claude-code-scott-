"""
Cloud Agent Orchestrator — 雲端 AI 代理系統
============================================
架構：
  本地層（數據收集 + 結果存儲 + 回調）
    ↕  MiniMax API（M2.7 作為 AI 大腦）
  雲端層（Claude 風格的多代理協調 + 任務規劃）
  回調層（飛書推送 + 郵件通知）

觸發方式：
  1. HTTP POST /webhook/task   → WebHook 觸發
  2. HTTP GET  /cron/daily     → Cron 排程觸發
  3. python run_agent.py --task → 本地 CLI 觸發

Example:
  # CLI 觸發
  python cloud_agent/run_agent.py --task "分析今日 PSAT 市場動態"

  # WebHook（外部觸發）
  curl -X POST http://localhost:8080/webhook/task \
    -H "Content-Type: application/json" \
    -d '{"task":"分析 AMD 新發布產品","trigger":"webhook"}'

  # Cron（每日早上 9 點自動執行）
  python cloud_agent/run_agent.py --cron --time "09:00"
"""

import os, sys, json, logging, time, threading, traceback
from pathlib import Path
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional
from enum import Enum

# ─── 設置路徑 ────────────────────────────────────────────────────────────────
AGENT_DIR = Path(__file__).parent.resolve()
ROOT_DIR  = AGENT_DIR.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    encoding="utf-8",
)
log = logging.getLogger("CloudAgent")

# ═══════════════════════════════════════════════════════════════════════════
# 配置加載
# ═══════════════════════════════════════════════════════════════════════════

def load_config() -> dict:
    cfg_file = AGENT_DIR / "config.yaml"
    if not cfg_file.exists():
        log.error(f"配置文件不存在: {cfg_file}")
        raise FileNotFoundError(cfg_file)

    import yaml
    with open(cfg_file, encoding="utf-8") as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# ═══════════════════════════════════════════════════════════════════════════
# 核心數據模型
# ═══════════════════════════════════════════════════════════════════════════

class TaskStatus(Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
    TIMEOUT   = "timeout"

class TaskPriority(Enum):
    LOW    = "low"
    NORMAL = "normal"
    HIGH   = "high"
    CRITICAL = "critical"

@dataclass
class Task:
    id:         str
    prompt:     str
    priority:   str = "normal"
    trigger:    str = "cli"        # cli | webhook | cron
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status:     str = "pending"
    result:     Optional[dict] = None
    error:      Optional[str] = None
    started_at: Optional[str] = None
    finished_at:Optional[str] = None
    duration_s: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 2

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value if isinstance(self.status, TaskStatus) else self.status
        return d

    @property
    def status_enum(self) -> TaskStatus:
        if isinstance(self.status, str):
            return TaskStatus(self.status)
        return self.status

# ═══════════════════════════════════════════════════════════════════════════
# MiniMax API 客戶端
# ═══════════════════════════════════════════════════════════════════════════

class MiniMaxClient:
    """MiniMax API（M2.7）封裝"""

    def  __init__(self, cfg: dict):
        self.api_key  = cfg["minimax"]["api_key"]
        self.base_url = cfg["minimax"]["base_url"]
        self.model    = cfg["minimax"].get("model", "MiniMax-Text-01")
        self.max_tokens = cfg["minimax"].get("max_tokens", 8192)
        self.temperature = cfg["minimax"].get("temperature", 0.7)
        self.timeout  = cfg["minimax"].get("timeout", 120)
        log.info(f"MiniMax Client 初始化: model={self.model}, max_tokens={self.max_tokens}")

    def chat(self, prompt: str, system_prompt: str = "", context: list = None) -> str:
        """發送對話請求到 MiniMax API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        url = f"{self.base_url}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        start = time.time()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, headers=headers, json=payload)

            elapsed = time.time() - start

            if resp.status_code == 200:
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                log.info(f"[MiniMax] 回應耗時 {elapsed:.1f}s | tokens: {usage.get('total_tokens', '?')}")
                return content
            else:
                log.error(f"[MiniMax] HTTP {resp.status_code}: {resp.text[:300]}")
                raise RuntimeError(f"MiniMax API 錯誤: {resp.status_code}")

        except httpx.TimeoutException:
            log.error(f"[MiniMax] 請求超時 ({self.timeout}s)")
            raise RuntimeError(f"MiniMax API 請求超時")
        except Exception as e:
            log.error(f"[MiniMax] 異常: {e}")
            raise

# ═══════════════════════════════════════════════════════════════════════════
# 結果存儲器
# ═══════════════════════════════════════════════════════════════════════════

class ResultStore:
    """本地結果持久化"""

    def __init__(self, store_dir: Path):
        self.store_dir = store_dir
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir  = store_dir / "tasks"
        self.results_dir = store_dir / "results"
        self.tasks_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        log.info(f"ResultStore 初始化: {store_dir}")

    def save_task(self, task: Task) -> Path:
        """保存任務元數據"""
        fpath = self.tasks_dir / f"{task.id}.json"
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
        return fpath

    def save_result(self, task: Task, content: str) -> Path:
        """保存任務結果內容"""
        fpath = self.results_dir / f"{task.id}.txt"
        meta_path = self.results_dir / f"{task.id}_meta.json"

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "task_id": task.id,
                "prompt": task.prompt,
                "status": task.status_enum.value,
                "duration_s": task.duration_s,
                "finished_at": task.finished_at,
                "trigger": task.trigger,
            }, f, ensure_ascii=False, indent=2)

        return fpath

    def list_tasks(self, limit: int = 50) -> list[Task]:
        """列出最近任務"""
        tasks = []
        for f in sorted(self.tasks_dir.glob("*.json"), reverse=True)[:limit]:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
                tasks.append(Task(**d))
        return tasks

    def get_task(self, task_id: str) -> Optional[Task]:
        fpath = self.tasks_dir / f"{task_id}.json"
        if not fpath.exists():
            return None
        with open(fpath, encoding="utf-8") as f:
            return Task(**json.load(f))

    def get_result(self, task_id: str) -> Optional[str]:
        fpath = self.results_dir / f"{task_id}.txt"
        if not fpath.exists():
            return None
        with open(fpath, encoding="utf-8") as f:
            return f.read()

# ═══════════════════════════════════════════════════════════════════════════
# 飛書通知器
# ═══════════════════════════════════════════════════════════════════════════

class FeishuNotifier:
    """飛書文檔 + 消息通知"""

    def __init__(self, cfg: dict, mm_client: MiniMaxClient, store: ResultStore):
        self.cfg  = cfg
        self.mm   = mm_client
        self.store = store
        self.doc_id = cfg.get("feishu", {}).get("doc_id", "")
        self.sheet_id = cfg.get("feishu", {}).get("sheet_id", "")
        self.lark_cli = "lark-cli"   # 假設 lark-cli 在 PATH 中

    def notify(self, task: Task, result_content: str) -> bool:
        """發送任務完成通知"""
        try:
            summary = result_content[:500] + ("..." if len(result_content) > 500 else "")
            msg = (
                f"✅ 任務完成\n"
                f"ID：{task.id}\n"
                f"觸發：{task.trigger}\n"
                f"耗時：{task.duration_s:.1f}s\n"
                f"狀態：{task.status_enum.value}\n"
                f"\n結果摘要：\n{summary}"
            )
            log.info(f"[Feishu] 通知內容已準備，實際發送請配置 lark-cli")
            return True
        except Exception as e:
            log.error(f"[Feishu] 通知失敗: {e}")
            return False

# ═══════════════════════════════════════════════════════════════════════════
# 郵件通知器
# ═══════════════════════════════════════════════════════════════════════════

class EmailNotifier:
    """電子郵件通知"""

    def __init__(self, cfg: dict):
        import smtplib, ssl
        self.cfg = cfg
        self.email_cfg = cfg.get("email", {})

    def send(self, task: Task, result_content: str) -> bool:
        """發送郵件通知"""
        try:
            import smtplib, ssl
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            smtp_server = self.email_cfg["smtp_server"]
            smtp_port   = self.email_cfg["smtp_port"]
            username    = self.email_cfg["sender"]
            password    = self.email_cfg["password"]
            recipients  = self.email_cfg.get("recipient", "").split(",")

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[CloudAgent] 任務完成: {task.id[:8]} — {task.prompt[:40]}"
            msg["From"] = username
            msg["To"] = ",".join(r.strip() for r in recipients)

            body = (
                f"Cloud Agent 任務完成通知\n"
                f"{'='*50}\n"
                f"任務 ID：{task.id}\n"
                f"觸發方式：{task.trigger}\n"
                f"創建時間：{task.created_at}\n"
                f"完成時間：{task.finished_at}\n"
                f"耗時：{task.duration_s:.1f} 秒\n"
                f"狀態：{task.status_enum.value}\n"
                f"\n{'='*50}\n"
                f"任務描述：{task.prompt}\n"
                f"\n{'='*50}\n"
                f"完整結果：\n{result_content}\n"
            )
            msg.attach(MIMEText(body, "plain", "utf-8"))

            with smtplib.SMTP_SSL(smtp_server, smtp_port,
                                   context=ssl.create_default_context()) as server:
                server.login(username, password)
                server.sendmail(username, recipients, msg.as_string())

            log.info(f"[Email] 已發送至 {recipients}")
            return True

        except Exception as e:
            log.error(f"[Email] 發送失敗: {e}")
            traceback.print_exc()
            return False

# ═══════════════════════════════════════════════════════════════════════════
# 雲端代理核心引擎
# ═══════════════════════════════════════════════════════════════════════════

class CloudAgentEngine:
    """
    雲端 AI 代理引擎
    = 雲端 MiniMax（M2.7）負責：任務分析、步驟規劃、判斷決策
    = 本地組件負責：數據收集、存儲、回調通知
    """

    SYSTEM_PROMPT = """你是一個專業的 AI 任務代理引擎。收到任務描述後，你需要：

1. **理解任務**：分析用戶需求的意圖、範圍、預期輸出
2. **規劃步驟**：將任務分解為可執行的子步驟
3. **執行判斷**：對每個步驟做出決策（是否需要搜索、代碼、數據處理等）
4. **整合輸出**：將所有子任務的結果整合為完整的交付物

你的輸出格式：
- 先說明你的分析思路和執行計劃
- 然後逐步執行每個步驟
- 最後輸出完整結論和交付物

如果任務超出能力範圍，明確說明並建議替代方案。
重要：使用繁體中文回答。"""

    def __init__(self, cfg: dict):
        self.cfg   = cfg
        self.mm    = MiniMaxClient(cfg)
        store_dir  = Path(cfg.get("storage", {}).get("dir", str(AGENT_DIR / "store")))
        self.store = ResultStore(store_dir)
        self.email = EmailNotifier(cfg)
        self.feishu = FeishuNotifier(cfg, self.mm, self.store)
        self._task_lock = threading.Lock()

    def _generate_task_id(self) -> str:
        import uuid
        return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    def run_task(self, prompt: str, trigger: str = "cli",
                 priority: str = "normal",
                 wait_result: bool = True) -> Task:
        """執行單個任務（同步）"""
        task_id = self._generate_task_id()
        task = Task(
            id=task_id,
            prompt=prompt,
            trigger=trigger,
            priority=priority,
            status=TaskStatus.PENDING,
        )

        # 嘗試恢復
        existing = self.store.get_task(task_id)
        if existing:
            task = existing
        else:
            self.store.save_task(task)

        log.info(f"[Engine] 開始任務 {task_id}: {prompt[:80]}")
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        self.store.save_task(task)

        start = time.time()
        try:
            result = self.mm.chat(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
            )
            task.duration_s = time.time() - start
            task.finished_at = datetime.now().isoformat()
            task.result = {"content_length": len(result)}
            task.status = TaskStatus.SUCCESS

            # 保存結果
            self.store.save_result(task, result)
            self.store.save_task(task)

            # 回調通知
            self._send_notifications(task, result)

            log.info(f"[Engine] 任務 {task_id} 完成，耗時 {task.duration_s:.1f}s")

        except Exception as e:
            task.duration_s = time.time() - start
            task.finished_at = datetime.now().isoformat()
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.store.save_task(task)
            log.error(f"[Engine] 任務 {task_id} 失敗: {e}")

        return task

    def run_parallel(self, prompts: list[str], trigger: str = "cli") -> list[Task]:
        """並行執行多個任務（多代理）"""
        threads = []
        results = []

        def _run(prompt):
            t = self.run_task(prompt, trigger=trigger)
            results.append(t)

        for p in prompts:
            t = threading.Thread(target=_run, args=(p,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return results

    def _send_notifications(self, task: Task, result_content: str):
        """發送回調通知"""
        # 郵件通知
        if self.cfg.get("notification", {}).get("email", {}).get("enabled", True):
            threading.Thread(
                target=lambda: self.email.send(task, result_content),
                daemon=True
            ).start()

        # 飛書通知
        if self.cfg.get("notification", {}).get("feishu", {}).get("enabled", False):
            threading.Thread(
                target=lambda: self.feishu.notify(task, result_content),
                daemon=True
            ).start()

    def get_status(self, task_id: str) -> dict:
        """查詢任務狀態"""
        task = self.store.get_task(task_id)
        if not task:
            return {"error": "任務不存在"}
        return {
            "id": task.id,
            "status": task.status_enum.value,
            "prompt": task.prompt,
            "duration_s": task.duration_s,
            "trigger": task.trigger,
        }

# ═══════════════════════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cloud Agent CLI")
    sub = parser.add_subparsers(dest="cmd")

    # 單任務執行
    run_p = sub.add_parser("run", help="執行單個任務")
    run_p.add_argument("--task", "-t", required=True, help="任務描述")
    run_p.add_argument("--priority", default="normal", choices=["low","normal","high","critical"])
    run_p.add_argument("--trigger", default="cli")
    run_p.add_argument("--output", "-o", help="結果輸出文件")

    # 多代理並行
    multi_p = sub.add_parser("multi", help="並行執行多個任務")
    multi_p.add_argument("--tasks", "-t", required=True, help="任務描述（多行，用 | 分隔）")
    multi_p.add_argument("--trigger", default="cli")

    # 任務管理
    list_p = sub.add_parser("list", help="列出最近任務")
    list_p.add_argument("--limit", "-n", type=int, default=20)

    status_p = sub.add_parser("status", help="查詢任務狀態")
    status_p.add_argument("task_id", help="任務 ID")

    result_p = sub.add_parser("result", help="查看任務結果")
    result_p.add_argument("task_id", help="任務 ID")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return

    engine = CloudAgentEngine(CONFIG)

    if args.cmd == "run":
        task = engine.run_task(args.task, trigger=args.trigger, priority=args.priority)
        print(f"\n{'='*60}")
        print(f"任務 ID：{task.id}")
        print(f"狀態：{task.status_enum.value}")
        print(f"耗時：{task.duration_s:.1f}s")
        print(f"{'='*60}")

        result = engine.store.get_result(task.id)
        if result:
            print(f"\n【AI 回應】\n{result[:2000]}")
            if len(result) > 2000:
                print(f"\n...（還有 {len(result)-2000} 字，請用 `result {task.id}` 查看完整內容）")

        if args.output and result:
            Path(args.output).write_text(result, encoding="utf-8")
            print(f"\n結果已保存至：{args.output}")

    elif args.cmd == "multi":
        prompts = [p.strip() for p in args.tasks.split("|") if p.strip()]
        print(f"並行執行 {len(prompts)} 個任務...")
        tasks = engine.run_parallel(prompts, trigger=args.trigger)
        print(f"\n{'='*60}")
        print(f"完成 {len(tasks)} 個任務")
        for t in tasks:
            print(f"  {t.id[:20]}... | {t.status_enum.value} | {t.duration_s:.1f}s")

    elif args.cmd == "list":
        tasks = engine.store.list_tasks(limit=args.limit)
        print(f"\n{'='*60}")
        print(f"最近 {len(tasks)} 個任務")
        print(f"{'ID':<30} {'狀態':<10} {'耗時':<8} {'觸發':<8} {'描述'}")
        print("-"*60)
        for t in tasks:
            print(f"{t.id:<30} {t.status_enum.value:<10} {str(t.duration_s or '-'):<8} {t.trigger:<8} {t.prompt[:40]}")

    elif args.cmd == "status":
        status = engine.get_status(args.task_id)
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.cmd == "result":
        result = engine.store.get_result(args.task_id)
        if result:
            print(result)
        else:
            print(f"任務 {args.task_id} 結果不存在")

if __name__ == "__main__":
    main()
