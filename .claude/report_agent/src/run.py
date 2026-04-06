"""
Report Agent - 執行入口
用法:
  python run.py                  # 完整流程
  python run.py --mode aggregate # 只匯總
  python run.py --mode html      # 只生成 HTML
  python run.py --mode excel     # 只生成 Excel
  python run.py --mode distribute # 分發報告
  python run.py --mode scheduler # 排程模式
"""
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent  # → .claude/
sys.path.insert(0, str(_ROOT))

import asyncio
import argparse
from pathlib import Path
from core import setup_logger, load_config
from report_agent.src.executor import ReportExecutor


def main():
    parser = argparse.ArgumentParser(description="Report Agent")
    parser.add_argument("--mode", default="full",
                        choices=["full", "aggregate", "html", "excel", "pdf", "lark", "distribute", "scheduler"],
                        help="執行模式")
    args = parser.parse_args()

    agent_dir = Path(__file__).resolve().parent.parent  # → report_agent/
    cfg = load_config(config_path=str(agent_dir / "config/settings.json"))
    setup_logger("report_agent", level="INFO", log_dir=str(agent_dir / "logs"))

    executor = ReportExecutor(cfg)

    if args.mode == "scheduler":
        from core import TaskScheduler
        scheduler = TaskScheduler(cfg)
        schedule = cfg.get("schedule", "0 10 * * 1-5")
        scheduler.add_cron_task("daily_report", executor.run, schedule)
        scheduler.start()
        print("Report Agent 排程已啟動，按 Ctrl+C 停止")
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            scheduler.shutdown()
    else:
        result = executor.run(mode=args.mode)
        print(f"執行完成: {result.get('status', 'unknown')}")


if __name__ == "__main__":
    main()
