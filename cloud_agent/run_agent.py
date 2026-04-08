#!/usr/bin/env python3
"""
Cloud Agent — 雲端 AI 代理 CLI 統一入口
=========================================

用法：
  python cloud_agent/run_agent.py run --task "分析 AMD 新產品"
  python cloud_agent/run_agent.py multi --tasks "分析AMD|分析Intel|分析NVIDIA"
  python cloud_agent/run_agent.py server --port 8080
  python cloud_agent/run_agent.py cron --schedule "09:00"
  python cloud_agent/run_agent.py list
  python cloud_agent/run_agent.py status <task_id>
  python cloud_agent/run_agent.py result <task_id>
"""

import sys, os, logging
from pathlib import Path

# 確保項目根目錄在路徑中
_ROOT = Path(__file__).parent.resolve().parent.resolve()  # d:/claude mini max 2.7/
sys.path.insert(0, str(_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
log = logging.getLogger("CloudAgent.Main")

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Cloud Agent — 雲端 AI 代理系統",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python cloud_agent/run_agent.py run --task "分析 2025 年 CPU 市場動態"
  python cloud_agent/run_agent.py multi --tasks "AMD 分析|Intel 分析|NVIDIA 分析"
  python cloud_agent/run_agent.py server --port 8080
  curl -X POST http://localhost:8080/webhook/task -H "Content-Type: application/json" \\
       -d "{\"task\":\"分析今日 PSU 市場\"}"
  python cloud_agent/run_agent.py cron --schedule "09:00"
        """
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # ── run：執行單任務 ──────────────────────────────────────────────────
    run_p = sub.add_parser("run", help="執行單個 AI 任務")
    run_p.add_argument("--task", "-t", required=True, help="任務描述")
    run_p.add_argument("--priority", default="normal",
                       choices=["low","normal","high","critical"])
    run_p.add_argument("--output", "-o", help="結果輸出文件")
    run_p.add_argument("--trigger", default="cli")

    # ── multi：並行多任務 ────────────────────────────────────────────────
    multi_p = sub.add_parser("multi", help="並行執行多個 AI 任務")
    multi_p.add_argument("--tasks", "-t", required=True,
                        help="任務描述，多個用 | 分隔")
    multi_p.add_argument("--trigger", default="cli")

    # ── server：啟動 HTTP 服務器 ──────────────────────────────────────────
    srv_p = sub.add_parser("server", help="啟動 HTTP 服務器（WebHook + Cron）")
    srv_p.add_argument("--host", default="0.0.0.0")
    srv_p.add_argument("--port", "-p", type=int, default=8080)

    # ── cron：設置每日 Cron 任務 ────────────────────────────────────────
    cron_p = sub.add_parser("cron", help="設置每日自動執行")
    cron_p.add_argument("--schedule", "-s",
                        default="09:00",
                        help="執行時間（HH:MM）")
    cron_p.add_argument("--once", action="store_true",
                        help="僅執行一次（不註冊 Cron）")

    # ── list：任務列表 ─────────────────────────────────────────────────
    list_p = sub.add_parser("list", help="列出最近任務")
    list_p.add_argument("--limit", "-n", type=int, default=20)

    # ── status：查詢狀態 ───────────────────────────────────────────────
    stat_p = sub.add_parser("status", help="查詢任務狀態")
    stat_p.add_argument("task_id")

    # ── result：查看結果 ────────────────────────────────────────────────
    res_p = sub.add_parser("result", help="查看任務結果")
    res_p.add_argument("task_id")

    args = parser.parse_args()

    # ── 延遲導入避免啟動慢 ───────────────────────────────────────────────
    from cloud_agent.orchestrator import (
        CloudAgentEngine, load_config, TaskStatus
    )

    engine = CloudAgentEngine(load_config())

    # ══════════════════════════════════════════════════════════════════════
    if args.cmd == "run":
        log.info(f"執行任務: {args.task[:80]}")
        task = engine.run_task(
            args.task,
            trigger=args.trigger,
            priority=args.priority,
        )

        print(f"\n{'='*60}")
        print(f"任務 ID：{task.id}")
        print(f"狀態：{task.status_enum.value}")
        print(f"耗時：{task.duration_s:.1f}s")
        print(f"{'='*60}")

        result = engine.store.get_result(task.id)
        if result:
            print(f"\n【AI 回應】\n{result[:3000]}")
            if len(result) > 3000:
                print(f"\n...（還有 {len(result)-3000} 字，"
                      f"請用 `result {task.id}` 查看完整內容）")

        if args.output and result:
            Path(args.output).write_text(result, encoding="utf-8")
            print(f"\n✅ 結果已保存至：{args.output}")

    # ══════════════════════════════════════════════════════════════════════
    elif args.cmd == "multi":
        prompts = [p.strip() for p in args.tasks.split("|") if p.strip()]
        print(f"🚀 並行執行 {len(prompts)} 個任務...")

        results = engine.run_parallel(prompts, trigger=args.trigger)

        print(f"\n{'='*60}")
        print(f"完成 {len(results)} 個任務：")
        for t in results:
            icon = "✅" if t.status_enum == TaskStatus.SUCCESS else "❌"
            print(f"  {icon} {t.id[:20]} | {t.status_enum.value:<10} "
                  f"| {t.duration_s:.1f}s | {t.prompt[:50]}")

    # ══════════════════════════════════════════════════════════════════════
    elif args.cmd == "server":
        log.info("啟動 HTTP 服務器...")
        from cloud_agent.http_server import start_server
        print(f"Cloud Agent HTTP Server")
        print(f"  WebHook：POST http://{args.host}:{args.port}/webhook/task")
        print(f"  Cron觸發：GET  http://{args.host}:{args.port}/cron/daily")
        print(f"  任務列表：GET  http://{args.host}:{args.port}/api/tasks")
        print(f"  健康檢查：GET  http://{args.host}:{args.port}/health")
        print()
        start_server(args.host, args.port)

    # ══════════════════════════════════════════════════════════════════════
    elif args.cmd == "cron":
        import time
        from datetime import datetime

        if args.once:
            log.info("執行一次每日報告...")
            template = load_config().get("agent_templates", {}).get(
                "daily_report", ""
            ).replace("{date}", datetime.now().strftime("%Y年%m月%d日"))
            task = engine.run_task(template, trigger="cron")
            print(f"✅ 任務完成: {task.id}")
            return

        log.info(f"設置每日 Cron 任務: {args.schedule}")
        print("""
╔══════════════════════════════════════════════════════════════╗
║  Cron 任務已配置                                          ║
║  建議使用 Windows Task Scheduler 或 cron 調用：            ║
║                                                          ║
║  Windows：                                                ║
║    schtasks /create /tn "CloudAgent.Daily" \\            ║
║             /tr "python cloud_agent/run_agent.py cron --once" \\ ║
║             /sc daily /st {args.schedule}                 ║
║                                                          ║
║  或直接運行服務器：                                      ║
║    python cloud_agent/run_agent.py server --port 8080    ║
╚══════════════════════════════════════════════════════════════╝
        """)

    # ══════════════════════════════════════════════════════════════════════
    elif args.cmd == "list":
        tasks = engine.store.list_tasks(limit=args.limit)
        print(f"\n{'='*75}")
        print(f"最近 {len(tasks)} 個任務")
        print(f"{'ID':<32} {'狀態':<10} {'耗時':<8} {'觸發':<8} 描述")
        print("-"*75)
        for t in tasks:
            icon = {"success":"✅","running":"🔄","failed":"❌","pending":"⏳"}.get(
                t.status_enum.value, "?")
            print(f"{icon} {t.id:<30} {t.status_enum.value:<10} "
                  f"{str(round(t.duration_s,1) if t.duration_s else '-'):<8} "
                  f"{t.trigger:<8} {t.prompt[:40]}")

    # ══════════════════════════════════════════════════════════════════════
    elif args.cmd == "status":
        status = engine.get_status(args.task_id)
        if "error" in status:
            print(f"❌ {status['error']}")
        else:
            print(f"\n{'='*50}")
            for k, v in status.items():
                print(f"  {k:<20} {v}")
            print(f"{'='*50}")

    # ══════════════════════════════════════════════════════════════════════
    elif args.cmd == "result":
        result = engine.store.get_result(args.task_id)
        if result:
            print(result)
        else:
            print(f"❌ 任務 {args.task_id} 的結果不存在")

if __name__ == "__main__":
    main()
