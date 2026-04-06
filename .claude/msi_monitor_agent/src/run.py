"""
MSI Monitor Agent - 執行入口
用法:
  python run.py                  # 完整流程
  python run.py --mode collect   # 收集 MSI 更新
  python run.py --mode diff      # 比對新舊更新
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
from msi_monitor_agent.src.executor import MsiMonitorExecutor


def main():
    parser = argparse.ArgumentParser(description="MSI Monitor Agent")
    parser.add_argument("--mode", default="full",
                        choices=["full", "collect", "diff", "report", "scheduler"],
                        help="執行模式")
    args = parser.parse_args()

    agent_dir = Path(__file__).resolve().parent.parent  # → msi_monitor_agent/
    cfg = load_config(config_path=str(agent_dir / "config/settings.json"))
    setup_logger("msi_monitor", level="INFO", log_dir=str(agent_dir / "logs"))

    executor = MsiMonitorExecutor(cfg)

    if args.mode == "scheduler":
        from core import TaskScheduler
        scheduler = TaskScheduler(cfg)
        scheduler.add_cron_task("daily_check", executor.run, cfg["crawling"]["schedule"])
        scheduler.start()
        print("MSI Monitor Agent 排程已啟動，按 Ctrl+C 停止")
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            scheduler.shutdown()
    else:
        result = asyncio.run(executor.run(mode=args.mode))
        print(f"執行完成: {result.get('status', 'unknown')}")


if __name__ == "__main__":
    main()
